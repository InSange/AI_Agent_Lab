from pathlib import Path
import importlib.util
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PROJECT_ROOT / "tools" / "harness_buddy.py"

EVALUATION_SAMPLES = [
    ("빨리 해줘", "fast"),
    ("대충 빨리 가자", "fast"),
    ("조심해서 해줘", "careful"),
    ("좀 불안한데", "careful"),
    ("검증해줘", "check"),
    ("테스트 돌려", "check"),
    ("상태 보여줘", "status"),
    ("지금 상태 어때", "status"),
    ("마무리해도 돼?", "review"),
    ("이거 믿어도 돼?", "review"),
]

AMBIGUOUS_SAMPLES = [
    ("뭔가 이상한데?", "careful 후보"),
    ("이거 가능해?", "unknown 후보"),
    ("뭐 하지?", "unknown 후보"),
]


def bool_label(value: bool) -> str:
    return "사용" if value else "없음"


def load_harness_buddy_module():
    spec = importlib.util.spec_from_file_location("harness_buddy", CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("harness_buddy.py를 import할 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    sys.modules["harness_buddy"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_harness_buddy_module()
    classifier_name = "rules"
    sample_classification = module.classify_nudge(EVALUATION_SAMPLES[0][0])

    print("Nudge 분류 평가")
    print(f"분류기: {classifier_name}")
    print(f"분류 방식: {sample_classification.method}")
    print(f"모델 사용: {bool_label(sample_classification.uses_model)}")

    passed = 0
    for user_input, expected_intent in EVALUATION_SAMPLES:
        classification = module.classify_nudge(user_input)
        actual_intent = classification.intent
        if actual_intent == expected_intent:
            print(f"[OK] {user_input} -> {actual_intent}")
            passed += 1
        else:
            print(f"[FAIL] {user_input} -> {actual_intent} (기대: {expected_intent})")

    total = len(EVALUATION_SAMPLES)
    print(f"정확도: {passed}/{total}")
    print(f"모델 사용: {bool_label(sample_classification.uses_model)}")

    print("후보 샘플")
    for user_input, expected_policy in AMBIGUOUS_SAMPLES:
        print(f"- {user_input} -> {expected_policy}")

    if passed != total:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
