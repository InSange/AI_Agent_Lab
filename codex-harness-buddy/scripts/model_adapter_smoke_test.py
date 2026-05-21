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

    if module.MODEL_PROVIDER != "rules":
        print("model adapter smoke test 실패: 기본 provider가 rules가 아닙니다.")
        return 1

    model_info = module.get_model_info()
    expected_info = {
        "provider": "rules",
        "model": "none",
        "uses_model": False,
        "status": "ready",
        "note": "Hugging Face 모델은 아직 연결되지 않았습니다.",
    }
    if model_info != expected_info:
        print("model adapter smoke test 실패: model info가 예상과 다릅니다.")
        print(f"- 기대: {expected_info}")
        print(f"- 실제: {model_info}")
        return 1

    checks = [
        ("빨리 해줘", "fast", "python tools/harness_buddy.py prompt fast"),
        ("조심해서 해줘", "careful", "python tools/harness_buddy.py prompt careful"),
        ("검증해줘", "check", "python tools/harness_buddy.py check"),
        ("지금 상태 어때", "status", "python tools/harness_buddy.py status"),
        ("마무리해도 돼?", "review", "python tools/harness_buddy.py review"),
    ]

    for user_input, expected_intent, expected_command in checks:
        result = module.classify_intent(user_input, provider="rules")
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
        if result.confidence is not None:
            print("model adapter smoke test 실패: rules provider confidence는 없어야 합니다.")
            return 1

    hf_info = module.get_model_info("hf")
    if hf_info["provider"] != "hf":
        print("model adapter smoke test 실패: hf provider 정보가 예상과 다릅니다.")
        return 1
    if hf_info["model"] != module.HF_MODEL_ID:
        print("model adapter smoke test 실패: hf 모델 ID가 예상과 다릅니다.")
        return 1
    if hf_info["status"] not in ["ready", "missing_dependencies"]:
        print("model adapter smoke test 실패: hf provider 상태가 예상 범위가 아닙니다.")
        print(f"- 실제: {hf_info['status']}")
        return 1

    unknown_result = module.classify_intent("빨리 해줘", provider="unknown")
    if unknown_result.method != "알 수 없는 provider" or unknown_result.uses_model:
        print("model adapter smoke test 실패: 알 수 없는 provider 응답이 예상과 다릅니다.")
        return 1

    print("model adapter smoke test 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
