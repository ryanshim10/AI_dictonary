import shutil
import time
from pathlib import Path
from typing import List, Tuple, Callable, Optional

from .config import resolve_rel
from .stt_whispercpp import extract_audio, chunk_audio, transcribe_all
from .llm_client import call_llm
from . import prompts


def _safe_name(p: Path) -> str:
    s = p.stem
    return "".join([c if c.isalnum() or c in "-_" else "_" for c in s])


def mmss(seconds: int) -> str:
    return f"{seconds//60:02d}:{seconds%60:02d}"


def process_one(mp4_path: str, base_dir: str, out_root: str, cfg_path: str, log: Callable[[str], None]) -> str:
    """Process a single MP4 file. Returns output dir path."""

    from .config import load_config
    cfg = load_config(cfg_path)

    llm_cfg = cfg["llm"]
    stt_cfg = cfg["stt"]
    out_cfg = cfg.get("output", {})

    # Resolve tools
    ffmpeg = resolve_rel(base_dir, stt_cfg.get("ffmpeg", "bin/ffmpeg.exe"))
    whisper_cli = resolve_rel(base_dir, stt_cfg.get("whisper_cli", "bin/whisper-cli.exe"))
    whisper_model = resolve_rel(base_dir, stt_cfg.get("whisper_model", "models/ggml-small.bin"))
    language = (stt_cfg.get("language") or "ko").strip()
    chunk_seconds = int(stt_cfg.get("chunk_seconds") or 300)

    # fallback to system ffmpeg if configured path missing
    if not Path(ffmpeg).exists():
        ffmpeg = shutil.which("ffmpeg") or ffmpeg

    if not Path(ffmpeg).exists():
        raise RuntimeError(f"ffmpeg not found: {ffmpeg}")
    if not Path(whisper_cli).exists():
        raise RuntimeError(f"whisper-cli not found: {whisper_cli}")
    if not Path(whisper_model).exists():
        raise RuntimeError(f"whisper model not found: {whisper_model}")

    in_path = Path(mp4_path)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_dir = Path(out_root) / f"{_safe_name(in_path)}_{ts}"
    chunks_dir = out_dir / "chunks"
    out_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(exist_ok=True)

    log(f"[1/4] Audio extract: {in_path.name}")
    wav_path = str(out_dir / "audio.wav")
    extract_audio(ffmpeg, str(in_path), wav_path)

    log(f"[2/4] Chunking: {chunk_seconds}s")
    chunk_audio(ffmpeg, wav_path, str(chunks_dir), chunk_seconds)

    log(f"[3/4] STT (whisper.cpp): {language}")
    transcribe_all(whisper_cli, whisper_model, str(chunks_dir), language=language)

    # Build timeline summaries
    log(f"[4/4] LLM summarize (mode={llm_cfg.get('mode','chat_completions')})")
    chunk_txts = sorted(chunks_dir.glob("chunk*.txt"))
    timeline_lines: List[str] = ["# 5분 단위 요약\n"]

    for i, txt_path in enumerate(chunk_txts):
        start = i * chunk_seconds
        end = (i + 1) * chunk_seconds
        chunk_text = txt_path.read_text(encoding="utf-8").strip()
        if not chunk_text:
            timeline_lines.append(f"## {mmss(start)}~{mmss(end)}\n- (자막 없음)\n")
            continue

        prompt = prompts.prompt_chunk_summary_ko(chunk_text, start, end)
        summary = call_llm(llm_cfg, prompt)

        timeline_lines.append(f"## {mmss(start)}~{mmss(end)}\n{summary.strip()}\n")

    timeline_md = "\n".join(timeline_lines).strip() + "\n"
    (out_dir / "timeline_5min.md").write_text(timeline_md, encoding="utf-8")

    # Full summary
    full_prompt = prompts.prompt_full_summary_ko(timeline_md)
    full_md = call_llm(llm_cfg, full_prompt)
    (out_dir / "summary_full.md").write_text(full_md.strip() + "\n", encoding="utf-8")

    # CEO insights
    ceo_prompt = prompts.prompt_ceo_insights_ko(full_md)
    ceo_md = call_llm(llm_cfg, ceo_prompt)
    (out_dir / "ceo_insights.md").write_text(ceo_md.strip() + "\n", encoding="utf-8")

    # Optional: full transcript
    if (out_cfg.get("write_transcript_full") or "true").lower() in ("1","true","yes","on"):
        full_txt = "\n\n".join([p.read_text(encoding="utf-8").strip() for p in chunk_txts if p.exists()]).strip() + "\n"
        (out_dir / "transcript_full.txt").write_text(full_txt, encoding="utf-8")

    log(f"DONE: {out_dir}")
    return str(out_dir)
