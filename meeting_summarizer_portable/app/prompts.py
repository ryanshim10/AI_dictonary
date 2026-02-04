def prompt_chunk_summary_ko(chunk_text: str, start_sec: int, end_sec: int) -> str:
    mm = lambda s: f"{s//60:02d}:{s%60:02d}"
    return (
        "당신은 회의/세미나 요약 비서입니다.\n"
        "아래는 약 5분 분량의 자막입니다.\n"
        "규칙: (1) 핵심만, (2) 사실/발언 중심, (3) 과장 금지, (4) 한국어로.\n"
        "출력은 마크다운 bullet만.\n\n"
        f"구간: {mm(start_sec)}~{mm(end_sec)}\n\n"
        "[자막]\n"
        f"{chunk_text}\n"
    )


def prompt_full_summary_ko(timeline_md: str) -> str:
    return (
        "당신은 회의/세미나 기록을 정리하는 비서입니다.\n"
        "아래는 5분 단위 요약(타임라인)입니다. 이를 기반으로 전체 요약을 작성하세요.\n\n"
        "출력 형식(마크다운):\n"
        "# TL;DR (5줄)\n"
        "- ...\n\n"
        "# 상세 요약(주제별)\n"
        "## 주제 1\n- ...\n\n"
        "# 결정사항(Decision)\n- (없으면 '없음')\n\n"
        "# 액션아이템(Action items)\n- (담당/기한이 있으면 포함, 없으면 항목만)\n\n"
        "# 리스크/이슈\n- (없으면 '없음')\n\n"
        "주의: 없는 정보는 만들지 말 것.\n\n"
        "[타임라인]\n"
        f"{timeline_md}\n"
    )


def prompt_insights_ko(full_summary_md: str) -> str:
    return (
        "당신은 제조업(스마트팩토리/AX) 관점의 전략/실행 담당자입니다.\n"
        "아래 전체 요약을 바탕으로 'ROI + 실행체계' 중심으로 시사점을 정리하세요.\n\n"
        "출력 형식(마크다운):\n"
        "# 핵심 시사점(5줄)\n"
        "- ...\n\n"
        "# 사업/투자 시사점(ROI 관점)\n"
        "- 매출/원가/리드타임/OEE/불량/납기 관점으로 정리\n\n"
        "# 실행체계 시사점(조직/운영)\n"
        "- 데이터 소스/Owner, 운영(MLOps), 현장 적용/표준화, 변경관리, KPI 운영\n\n"
        "# 우선순위 제안 Top 5\n"
        "1. ...\n\n"
        "# 점검 질문 10개\n"
        "1) ...\n\n"
        "주의: 근거 없는 수치/사실은 만들지 말 것.\n\n"
        "[전체요약]\n"
        f"{full_summary_md}\n"
    )
