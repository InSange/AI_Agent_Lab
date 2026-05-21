from dataclasses import dataclass
import os


MODEL_PROVIDER = os.environ.get("HARNESS_BUDDY_MODEL_PROVIDER", "rules")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
HF_MODEL_ID = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
HF_NOT_CONNECTED_NOTE = "Hugging Face 모델은 아직 연결되지 않았습니다."
HF_CANDIDATE_LABELS = [
    "빠른 진행 요청",
    "불안해서 신중한 작업 요청",
    "믿어도 되는지 마무리해도 되는지 확인 요청",
    "검증 실행 요청",
    "상태 확인 요청",
]
HF_LABEL_TO_INTENT = {
    "빠른 진행 요청": ("fast", "python tools/harness_buddy.py prompt fast"),
    "불안해서 신중한 작업 요청": ("careful", "python tools/harness_buddy.py prompt careful"),
    "믿어도 되는지 마무리해도 되는지 확인 요청": ("review", "python tools/harness_buddy.py review"),
    "검증 실행 요청": ("check", "python tools/harness_buddy.py check"),
    "상태 확인 요청": ("status", "python tools/harness_buddy.py status"),
}
_HF_PIPELINE = None
HF_RULE_GUARD_THRESHOLD = 0.85


@dataclass(frozen=True)
class IntentClassification:
    intent: str
    reason: str
    next_command: str
    method: str = "키워드 규칙"
    uses_model: bool = False
    confidence: float | None = None


INTENT_RULES = [
    ("fast", ["빨리", "급해", "재촉", "닦달", "fast", "대충", "후딱"], "빠른 진행 요청으로 보임", "python tools/harness_buddy.py prompt fast"),
    ("check", ["검증", "테스트", "check", "돌려", "되는지", "되는지만"], "검증 실행 요청으로 보임", "python tools/harness_buddy.py check"),
    ("careful", ["조심", "꼼꼼", "위험", "승인", "careful", "불안", "천천히"], "신중한 작업 요청으로 보임", "python tools/harness_buddy.py prompt careful"),
    ("status", ["상태", "status", "어때", "현재", "어디까지", "진행상황"], "상태 확인 요청으로 보임", "python tools/harness_buddy.py status"),
    ("review", ["끝", "확인", "리뷰", "review", "됐어", "믿어도", "마무리", "괜찮아", "마지막"], "완료 여부 확인 요청으로 보임", "python tools/harness_buddy.py review"),
]


def get_model_info(provider: str = MODEL_PROVIDER) -> dict[str, object]:
    if provider == "rules":
        return {
            "provider": "rules",
            "model": "none",
            "uses_model": False,
            "status": "ready",
            "note": HF_NOT_CONNECTED_NOTE,
        }

    if provider == "hf":
        available = are_hf_dependencies_available()
        return {
            "provider": "hf",
            "model": HF_MODEL_ID,
            "uses_model": available,
            "status": "ready" if available else "missing_dependencies",
            "note": "Hugging Face provider를 사용할 수 있습니다." if available else "transformers 또는 torch가 설치되지 않았습니다.",
        }

    return {
        "provider": provider,
        "model": "none",
        "uses_model": False,
        "status": "unknown_provider",
        "note": "알 수 없는 provider입니다.",
    }


def classify_intent_with_rules(user_input: str) -> IntentClassification:
    lowered = user_input.lower()

    for intent, keywords, reason, next_command in INTENT_RULES:
        if any(keyword in lowered for keyword in keywords):
            return IntentClassification(intent=intent, reason=reason, next_command=next_command)

    return IntentClassification(
        intent="review",
        reason="명확한 의도를 찾지 못해 점검 요청으로 처리함",
        next_command="python tools/harness_buddy.py review",
    )


def are_hf_dependencies_available() -> bool:
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except ImportError:
        return False
    return True


def load_hf_pipeline():
    global _HF_PIPELINE
    if _HF_PIPELINE is None:
        from transformers import pipeline
        from transformers.utils import logging

        logging.set_verbosity_error()

        _HF_PIPELINE = pipeline("zero-shot-classification", model=HF_MODEL_ID)
    return _HF_PIPELINE


def classify_intent_with_hf(user_input: str) -> IntentClassification:
    try:
        classifier = load_hf_pipeline()
        result = classifier(user_input, candidate_labels=HF_CANDIDATE_LABELS, hypothesis_template="이 요청은 {}입니다.")
    except Exception as exc:
        fallback = classify_intent_with_rules(user_input)
        return IntentClassification(
            intent=fallback.intent,
            reason=f"Hugging Face provider 실패로 rules fallback 사용: {exc.__class__.__name__}",
            next_command=fallback.next_command,
            method="HF fallback",
            uses_model=False,
        )

    label = str(result["labels"][0])
    score = float(result["scores"][0])
    intent, next_command = HF_LABEL_TO_INTENT.get(label, ("review", "python tools/harness_buddy.py review"))
    rule_result = classify_intent_with_rules(user_input)
    if rule_result.intent in {"careful", "review"} and rule_result.intent != intent and score < HF_RULE_GUARD_THRESHOLD:
        return IntentClassification(
            intent=rule_result.intent,
            reason=f"HF confidence가 낮아 rules 보정 사용: {label} ({score:.2f})",
            next_command=rule_result.next_command,
            method="Hugging Face zero-shot + rules guard",
            uses_model=True,
            confidence=score,
        )

    return IntentClassification(
        intent=intent,
        reason=f"HF zero-shot 분류 결과: {label} ({score:.2f})",
        next_command=next_command,
        method="Hugging Face zero-shot",
        uses_model=True,
        confidence=score,
    )


def classify_intent(user_input: str, provider: str = MODEL_PROVIDER) -> IntentClassification:
    if provider == "rules":
        return classify_intent_with_rules(user_input)

    if provider == "hf":
        return classify_intent_with_hf(user_input)

    return IntentClassification(
        intent="review",
        reason="알 수 없는 provider입니다. rules provider를 사용해 주세요.",
        next_command="python tools/harness_buddy.py review",
        method="알 수 없는 provider",
        uses_model=False,
    )
