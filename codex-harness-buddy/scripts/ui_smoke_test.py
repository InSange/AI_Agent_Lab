import importlib.util
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_PATH = PROJECT_ROOT / "tools" / "buddy_ui.py"

EXPECTED_COMMANDS = {
    "Check": ["check"],
    "Status": ["status"],
    "Review Status": ["review"],
    "Fast": ["prompt", "fast"],
    "Careful": ["prompt", "careful"],
    "Review Prompt": ["prompt", "review"],
}

EXPECTED_BUTTON_GROUPS = [
    ("상태", ["Check", "Status", "Review Status"]),
    ("프롬프트", ["Fast", "Careful", "Review Prompt"]),
]


def load_ui_module():
    spec = importlib.util.spec_from_file_location("buddy_ui", UI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("buddy_ui.py를 import할 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    sys.modules["buddy_ui"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    try:
        import tkinter  # noqa: F401
    except Exception as exc:
        print(f"ui smoke test 실패: tkinter를 import할 수 없습니다. {exc}")
        return 1

    if not UI_PATH.exists():
        print("ui smoke test 실패: tools/buddy_ui.py가 없습니다.")
        return 1

    module = load_ui_module()

    if getattr(module, "WINDOW_TITLE", None) != "Codex Harness Buddy":
        print("ui smoke test 실패: 창 제목 상수가 예상과 다릅니다.")
        return 1

    if getattr(module, "COPY_BUTTON_LABEL", None) != "Copy Output":
        print("ui smoke test 실패: 복사 버튼 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "COPY_PROMPT_BUTTON_LABEL", None) != "Copy Prompt":
        print("ui smoke test 실패: 프롬프트 복사 버튼 라벨이 예상과 다릅니다.")
        return 1

    commands = getattr(module, "BUTTON_COMMANDS", None)
    if commands != EXPECTED_COMMANDS:
        print("ui smoke test 실패: 버튼 명령 계약이 예상과 다릅니다.")
        print(f"- 기대: {EXPECTED_COMMANDS}")
        print(f"- 실제: {commands}")
        return 1

    groups = getattr(module, "BUTTON_GROUPS", None)
    if groups != EXPECTED_BUTTON_GROUPS:
        print("ui smoke test 실패: 버튼 그룹 계약이 예상과 다릅니다.")
        print(f"- 기대: {EXPECTED_BUTTON_GROUPS}")
        print(f"- 실제: {groups}")
        return 1

    if not hasattr(module, "build_cli_command"):
        print("ui smoke test 실패: build_cli_command 함수가 없습니다.")
        return 1

    if module.build_cli_command(["status"])[-2:] != ["harness_buddy.py", "status"]:
        print("ui smoke test 실패: status CLI 명령 생성이 예상과 다릅니다.")
        return 1

    if module.command_label(["prompt", "fast"]) != "prompt fast":
        print("ui smoke test 실패: 명령 라벨 생성이 예상과 다릅니다.")
        return 1

    if module.running_status(["check"]) != "실행 중: check":
        print("ui smoke test 실패: 실행 중 상태 문구가 예상과 다릅니다.")
        return 1

    if module.completed_status(["check"], 0) != "완료: check":
        print("ui smoke test 실패: 성공 상태 문구가 예상과 다릅니다.")
        return 1

    if module.completed_status(["check"], 1) != "실패: check":
        print("ui smoke test 실패: 실패 상태 문구가 예상과 다릅니다.")
        return 1

    if module.copy_status() != "완료: 출력 복사":
        print("ui smoke test 실패: 복사 완료 상태 문구가 예상과 다릅니다.")
        return 1

    if module.copy_prompt_status() != "완료: 프롬프트 복사":
        print("ui smoke test 실패: 프롬프트 복사 완료 상태 문구가 예상과 다릅니다.")
        return 1

    if module.missing_prompt_status() != "복사할 프롬프트가 없습니다":
        print("ui smoke test 실패: 프롬프트 없음 상태 문구가 예상과 다릅니다.")
        return 1

    if not module.missing_prompt_should_clear_clipboard():
        print("ui smoke test 실패: 프롬프트 없음 시 클립보드 비움 계약이 예상과 다릅니다.")
        return 1

    if module.cleared_clipboard_text() != "":
        print("ui smoke test 실패: 클립보드 비움 텍스트가 예상과 다릅니다.")
        return 1

    if module.clipboard_text("  hello\n") != "hello":
        print("ui smoke test 실패: 클립보드 텍스트 정리가 예상과 다릅니다.")
        return 1

    if module.clipboard_text("   ") != "":
        print("ui smoke test 실패: 빈 클립보드 텍스트 처리가 예상과 다릅니다.")
        return 1

    if not module.is_prompt_command(["prompt", "fast"]):
        print("ui smoke test 실패: prompt fast 명령을 프롬프트로 인식하지 못했습니다.")
        return 1

    if module.is_prompt_command(["review"]):
        print("ui smoke test 실패: review 점검 명령을 프롬프트로 잘못 인식했습니다.")
        return 1

    if not module.should_keep_prompt(["prompt", "careful"], 0):
        print("ui smoke test 실패: 성공한 prompt 명령의 프롬프트 유지 계약이 예상과 다릅니다.")
        return 1

    if module.should_keep_prompt(["prompt", "careful"], 1):
        print("ui smoke test 실패: 실패한 prompt 명령의 프롬프트 유지 계약이 예상과 다릅니다.")
        return 1

    if not module.should_clear_prompt(["check"], 0):
        print("ui smoke test 실패: check 후 프롬프트 비움 계약이 예상과 다릅니다.")
        return 1

    if not module.should_clear_prompt(["nudge", "검증해줘"], 0):
        print("ui smoke test 실패: nudge 후 프롬프트 비움 계약이 예상과 다릅니다.")
        return 1

    if module.should_clear_prompt(["prompt", "fast"], 0):
        print("ui smoke test 실패: prompt 성공 후 프롬프트 비움 계약이 예상과 다릅니다.")
        return 1

    if "[Fast 실행]" not in module.output_header("Fast", ["prompt", "fast"]):
        print("ui smoke test 실패: 출력 헤더가 버튼 실행을 표시하지 않습니다.")
        return 1

    if "Nudge 해석" not in module.nudge_header("빨리 해줘"):
        print("ui smoke test 실패: nudge 출력 헤더가 해석 표시를 포함하지 않습니다.")
        return 1

    if module.buddy_state_after("Check", 0) != "준비됨":
        print("ui smoke test 실패: Check 성공 후 Buddy 상태가 예상과 다릅니다.")
        return 1

    if module.buddy_state_after("Check", 1) != "점검 필요":
        print("ui smoke test 실패: Check 실패 후 Buddy 상태가 예상과 다릅니다.")
        return 1

    if module.buddy_state_after("Review Status", 0) != "검토 중":
        print("ui smoke test 실패: Review Status 후 Buddy 상태가 예상과 다릅니다.")
        return 1

    if module.buddy_state_after("Review Prompt", 0) != "리뷰 지시문 준비":
        print("ui smoke test 실패: Review Prompt 후 Buddy 상태가 예상과 다릅니다.")
        return 1

    if module.buddy_state_label("준비됨") != "Buddy 상태: 준비됨":
        print("ui smoke test 실패: Buddy 상태 라벨이 예상과 다릅니다.")
        return 1

    if "Buddy 상태: 준비됨" not in module.output_header("Check", ["check"], "준비됨"):
        print("ui smoke test 실패: 출력 헤더에 Buddy 상태가 포함되지 않습니다.")
        return 1

    if "Buddy 상태: 입력 해석됨" not in module.nudge_header("빨리 해줘", "입력 해석됨"):
        print("ui smoke test 실패: nudge 출력 헤더에 Buddy 상태가 포함되지 않습니다.")
        return 1

    print("ui smoke test 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
