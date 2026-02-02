# 제조 AI/DX 용어집 웹앱 (Glossary WebApp)

제조/스마트팩토리/품질/설비 맥락의 AI·DX 용어를 **검색/필터/수정/엑셀 다운로드/엑셀 업로드**로 관리하는 초경량 웹앱입니다.

- ✅ 설치 직후 **예제 100개** 포함(바로 검색 가능)
- ✅ 사용자 수정 즉시 반영(JSON 정본)
- ✅ 엑셀로 내려받기/대량 업로드
- ✅ (선택) Azure OpenAI 연동 시 “검색 결과 없으면 생성”

---

## 1) 빠른 실행(로컬)

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8080
```

브라우저 접속: http://localhost:8080

---

## 2) 사용 방법(현업용)

- 검색: 키워드 입력 → [검색] → 카드 클릭 → 상세 확인
- 수정: 상세에서 [수정] → 편집 → [저장]
- 엑셀 다운로드: 상단 [엑셀 다운로드]
- 엑셀 업로드: 파일 선택 → [일괄 업로드(xlsx)]

자세한 매뉴얼:
- **설치/운영 매뉴얼:** `INSTALL_MANUAL.md`
- **PPT(설치/운영/요약) 원고:** `PPT_SLIDES.md`
- **PPT(사용방법) 원고:** `PPT_USAGE_MANUAL.md`

---

## 3) 데이터 정본

- 정본 파일: `data/glossary.json`
- 백업 권장:
```bash
cp data/glossary.json data/glossary.backup.$(date +%Y%m%d_%H%M%S).json
```

---

## 4) (선택) Azure OpenAI 연동

1) `.env.example` → `.env` 복사
2) `.env`에 값 설정 (키/토큰은 절대 레포에 커밋 금지)

LLM 설정이 정상인지 확인:
- `GET /api/llm/status`

---

## 5) 엑셀 다운로드 API

- GUI 버튼: **엑셀 다운로드**
- API: `GET /api/export.xlsx`

---

## 보안 주의
- `.env`(API Key/토큰) 파일은 **절대 Git에 커밋하지 마세요.**
