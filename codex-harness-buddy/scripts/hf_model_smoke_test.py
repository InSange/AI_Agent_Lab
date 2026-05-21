import importlib.util
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = PROJECT_ROOT / "tools" / "buddy_model_adapter.py"
KNOWN_INTENTS = {"fast", "careful", "review", "check", "status"}
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")


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

    info = module.get_model_info("hf")
    if info["status"] != "ready":
        print("hf model smoke test 실패: Hugging Face provider가 준비되지 않았습니다.")
        print(f"- 상태: {info['status']}")
        print(f"- 안내: {info['note']}")
        return 1

    result = module.classify_intent("검증해줘", provider="hf")
    print("HF 모델 분류 결과")
    print(f"- intent: {result.intent}")
    print(f"- method: {result.method}")
    print(f"- uses_model: {result.uses_model}")
    print(f"- reason: {result.reason}")

    if not result.uses_model:
        print("hf model smoke test 실패: HF provider가 rules fallback으로 처리되었습니다.")
        return 1
    if result.intent not in KNOWN_INTENTS:
        print("hf model smoke test 실패: 알 수 없는 intent가 반환되었습니다.")
        return 1

    print("hf model smoke test 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
