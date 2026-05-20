from dataclasses import dataclass


@dataclass(frozen=True)
class IntentClassification:
    intent: str
    reason: str
    next_command: str
    method: str = "키워드 규칙"
    uses_model: bool = False


INTENT_RULES = [
    ("check", ["검증", "테스트", "check", "돌려", "되는지", "되는지만"], "검증 실행 요청으로 보임", "python tools/harness_buddy.py check"),
    ("careful", ["조심", "꼼꼼", "위험", "승인", "careful", "불안", "천천히"], "신중한 작업 요청으로 보임", "python tools/harness_buddy.py prompt careful"),
    ("review", ["끝", "확인", "리뷰", "review", "됐어", "믿어도", "마무리"], "완료 여부 확인 요청으로 보임", "python tools/harness_buddy.py review"),
    ("status", ["상태", "status", "어때", "현재"], "상태 확인 요청으로 보임", "python tools/harness_buddy.py status"),
    ("fast", ["빨리", "급해", "재촉", "닦달", "fast", "대충", "후딱"], "빠른 진행 요청으로 보임", "python tools/harness_buddy.py prompt fast"),
]


def classify_intent(user_input: str) -> IntentClassification:
    lowered = user_input.lower()

    for intent, keywords, reason, next_command in INTENT_RULES:
        if any(keyword in lowered for keyword in keywords):
            return IntentClassification(intent=intent, reason=reason, next_command=next_command)

    return IntentClassification(
        intent="review",
        reason="명확한 의도를 찾지 못해 점검 요청으로 처리함",
        next_command="python tools/harness_buddy.py review",
    )
