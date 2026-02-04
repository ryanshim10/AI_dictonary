# Meeting Summarizer (Portable, Windows)

사내 PC에서 MP4 회의/세미나 영상을 **5분 단위 자막(STT)** 으로 만들고, 사내 LLM(Azure OpenAI 포맷)을 호출해서

- `timeline_5min.md` (5분 단위 요약)
- `summary_full.md` (전체 요약)
- `ceo_insights.md` (대표이사 관점 시사점: ROI+실행체계 중심)

을 생성하는 도구입니다.

> 목표: **수정 용이(파이썬 위주)** + **사내 커스터마이징 가능(config 기반)**

---

## 0) 사전 준비(사내 PC)

### 필수
1. **Python 3.10+**
2. **PyQt5** (이미 설치되어 있다고 했으니 그대로 사용)
3. **ffmpeg.exe**
4. **whisper.cpp 실행파일** (`whisper-cli.exe`) + 모델 파일(ggml)

> 이 레포에는 바이너리/모델을 포함하지 않습니다. 사내 정책에 맞게 `bin/`, `models/`에 넣어주세요.

폴더 배치:
- `meeting_summarizer_portable/bin/ffmpeg.exe`
- `meeting_summarizer_portable/bin/whisper-cli.exe`
- `meeting_summarizer_portable/models/ggml-small.bin` (또는 medium)

---

## 1) 설정(config.ini)
`meeting_summarizer_portable/config.ini` 를 수정하세요.

- Chat Completions / Responses API 모두 지원
- api-key 헤더 / Bearer 인증 모두 지원

---

## 2) GUI 실행
```bat
cd meeting_summarizer_portable
python app\main_gui.py
```

---

## 3) CLI 실행(배치 처리)
```bat
cd meeting_summarizer_portable
python app\main_cli.py --input "input\my.mp4" --out out
```

여러 파일:
```bat
python app\main_cli.py --input "input\*.mp4" --out out
```

---

## 4) 출력물
입력 파일 1개당:

- `out/<파일명>_<timestamp>/timeline_5min.md`
- `out/<파일명>_<timestamp>/summary_full.md`
- `out/<파일명>_<timestamp>/ceo_insights.md`
- (선택) `chunks/*.srt`, `chunks/*.txt`, `transcript_full.txt`

---

## 5) 사내 LLM(H-Chat/Azure OpenAI 포맷) 예시
문서 기준 예시:
- chat_completions URL 예: `https://h-chat-api.autoever.com/v2/api/openai/deployments/gpt-4o-mini/chat/completions`
- Header: `api-key: ...`

> 실제 키는 절대 레포에 커밋하지 말고, 로컬 config.ini에만 입력하세요.
