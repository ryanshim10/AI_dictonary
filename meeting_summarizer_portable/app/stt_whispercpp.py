import os
import subprocess
from pathlib import Path
from typing import Optional


def run_cmd(cmd, cwd: Optional[str] = None):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed ({p.returncode}): {' '.join(cmd)}\n{p.stdout[-4000:]}")
    return p.stdout


def extract_audio(ffmpeg_path: str, mp4_path: str, wav_path: str):
    cmd = [ffmpeg_path, "-y", "-i", mp4_path, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav_path]
    run_cmd(cmd)


def chunk_audio(ffmpeg_path: str, wav_path: str, out_dir: str, chunk_seconds: int):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Segment into fixed chunks. Creates: chunk000.wav, chunk001.wav, ...
    cmd = [
        ffmpeg_path, "-y",
        "-i", wav_path,
        "-f", "segment",
        "-segment_time", str(chunk_seconds),
        "-c", "copy",
        str(out / "chunk%03d.wav"),
    ]
    run_cmd(cmd)


def transcribe_chunk(whisper_cli: str, model_path: str, wav_path: str, out_prefix: str, language: str = "ko"):
    # whisper-cli will write <out_prefix>.txt and <out_prefix>.srt when -osrt is set
    cmd = [
        whisper_cli,
        "-m", model_path,
        "-f", wav_path,
        "-l", language,
        "-osrt",
        "-of", out_prefix,
    ]
    run_cmd(cmd)


def transcribe_all(whisper_cli: str, model_path: str, chunks_dir: str, language: str = "ko"):
    cdir = Path(chunks_dir)
    for wav in sorted(cdir.glob("chunk*.wav")):
        base = wav.with_suffix("")
        out_prefix = str(base)
        txt = str(base) + ".txt"
        srt = str(base) + ".srt"
        if Path(txt).exists() and Path(srt).exists():
            continue
        transcribe_chunk(whisper_cli, model_path, str(wav), out_prefix, language=language)
