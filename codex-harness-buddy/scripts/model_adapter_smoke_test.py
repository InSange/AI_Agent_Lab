import importlib.util
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = PROJECT_ROOT / "tools" / "buddy_model_adapter.py"


def load_model_adapter_module():
    spec = importlib.util.spec_from_file_location("buddy_model_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("buddy_model_adapter.py를 import할 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    sys.modules["buddy_model_adapter"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_model_adapter_module()

    checks = [
        ("빨리 해줘", "fast", "python tools/harness_buddy.py prompt fast"),
        ("조심해서 해줘", "careful", "python tools/harness_buddy.py prompt careful"),
        ("검증해줘", "check", "python tools/harness_buddy.py check"),
        ("지금 상태 어때", "status", "python tools/harness_buddy.py status"),
        ("마무리해도 돼?", "review", "python tools/harness_buddy.py review"),
    ]

    for user_input, expected_intent, expected_command in checks:
        result = module.classify_intent(user_input)
        if result.intent != expected_intent:
            print("model adapter smoke test 실패: intent가 예상과 다릅니다.")
            print(f"- 입력: {user_input}")
            print(f"- 기대: {expected_intent}")
            print(f"- 실제: {result.intent}")
            return 1
        if result.next_command != expected_command:
            print("model adapter smoke test 실패: next_command가 예상과 다릅니다.")
            print(f"- 입력: {user_input}")
            print(f"- 기대: {expected_command}")
            print(f"- 실제: {result.next_command}")
            return 1
        if result.uses_model:
            print("model adapter smoke test 실패: 초기 어댑터는 모델을 사용하지 않아야 합니다.")
            return 1

    print("model adapter smoke test 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
