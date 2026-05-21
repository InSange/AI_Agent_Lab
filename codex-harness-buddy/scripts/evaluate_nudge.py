from pathlib import Path
import argparse
import importlib.util
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PROJECT_ROOT / "tools" / "harness_buddy.py"

EVALUATION_SAMPLES = [
    ("빨리 해줘", "fast"),
    ("대충 빨리 가자", "fast"),
    ("빨리 끝내줘", "fast"),
    ("후딱 가자", "fast"),
    ("조심해서 해줘", "careful"),
    ("좀 불안한데", "careful"),
    ("천천히 확인해줘", "careful"),
    ("위험한 부분 다시 봐줘", "careful"),
    ("검증해줘", "check"),
    ("테스트 돌려", "check"),
    ("돌려보고 말해줘", "check"),
    ("테스트 한번만 해줘", "check"),
    ("상태 보여줘", "status"),
    ("지금 상태 어때", "status"),
    ("지금 어디까지 됐어?", "status"),
    ("현재 진행상황 알려줘", "status"),
    ("마무리해도 돼?", "review"),
    ("이거 믿어도 돼?", "review"),
    ("끝내도 괜찮아?", "review"),
    ("마지막으로 한번 봐줘", "review"),
]

AMBIGUOUS_SAMPLES = [
    ("뭔가 이상한데?", "careful 후보"),
    ("이거 가능해?", "unknown 후보"),
    ("뭐 하지?", "unknown 후보"),
]


def bool_label(value: bool) -> str:
    return "사용" if value else "없음"


def confidence_label(value: float | None) -> str:
    if value is None:
        return "없음"
    return f"{value:.2f}"


def load_harness_buddy_module():
    spec = importlib.util.spec_from_file_location("harness_buddy", CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("harness_buddy.py를 import할 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    sys.modules["harness_buddy"] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex Harness Buddy nudge 분류 평가")
    parser.add_argument(
        "--model-provider",
        choices=["rules", "hf"],
        default="rules",
        help="평가할 모델 provider",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    module = load_harness_buddy_module()
    classifier_name = args.model_provider
    sample_classification = module.classify_nudge(EVALUATION_SAMPLES[0][0], provider=args.model_provider)

    print("Nudge 분류 평가")
    print(f"분류기: {classifier_name}")
    print(f"분류 방식: {sample_classification.method}")
    print(f"모델 사용: {bool_label(sample_classification.uses_model)}")
    print(f"confidence: {confidence_label(sample_classification.confidence)}")

    passed = 0
    for user_input, expected_intent in EVALUATION_SAMPLES:
        classification = module.classify_nudge(user_input, provider=args.model_provider)
        actual_intent = classification.intent
        confidence = f" confidence={confidence_label(classification.confidence)}"
        if actual_intent == expected_intent:
            print(f"[OK] {user_input} -> {actual_intent}{confidence}")
            passed += 1
        else:
            print(f"[FAIL] {user_input} -> {actual_intent} (기대: {expected_intent}){confidence}")

    total = len(EVALUATION_SAMPLES)
    print(f"정확도: {passed}/{total}")
    print(f"모델 사용: {bool_label(sample_classification.uses_model)}")

    print("후보 샘플")
    for user_input, expected_policy in AMBIGUOUS_SAMPLES:
        print(f"- {user_input} -> {expected_policy}")

    if args.model_provider == "hf" and not sample_classification.uses_model:
        return 1
    if args.model_provider == "rules" and passed != total:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
