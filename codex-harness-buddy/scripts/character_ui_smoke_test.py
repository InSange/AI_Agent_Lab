import importlib.util
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHARACTER_PATH = PROJECT_ROOT / "tools" / "buddy_character.py"

EXPECTED_FACES = {
    "ready": "(^_^)",
    "stale": "(-_-)",
    "waiting": "(._.)",
    "needs_review": "(>_<)",
}

EXPECTED_REACTIONS = {
    "ready": "좋아요. 검증은 최신이에요.",
    "stale": "검증이 조금 오래됐어요. 한 번 확인해볼까요?",
    "waiting": "아직 검증 기록을 기다리는 중이에요.",
    "needs_review": "점검이 필요해요. 실패 로그부터 볼게요.",
}

EXPECTED_PREVIEW_STATES = {
    "Ready": "ready",
    "Stale": "stale",
    "Waiting": "waiting",
    "Needs Review": "needs_review",
}


def load_character_module():
    spec = importlib.util.spec_from_file_location("buddy_character", CHARACTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("buddy_character.py를 import할 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    sys.modules["buddy_character"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    try:
        import tkinter  # noqa: F401
    except Exception as exc:
        print(f"character ui smoke test 실패: tkinter를 import할 수 없습니다. {exc}")
        return 1

    if not CHARACTER_PATH.exists():
        print("character ui smoke test 실패: tools/buddy_character.py가 없습니다.")
        return 1

    module = load_character_module()

    if getattr(module, "WINDOW_TITLE", None) != "Codex Harness Buddy Character":
        print("character ui smoke test 실패: 창 제목 상수가 예상과 다릅니다.")
        return 1

    if getattr(module, "WINDOW_GEOMETRY", None) != "430x455":
        print("character ui smoke test 실패: 창 크기 계약이 예상과 다릅니다.")
        return 1

    if getattr(module, "RESULT_WRAP_LENGTH", None) != 380:
        print("character ui smoke test 실패: 결과 문구 줄바꿈 폭이 예상과 다릅니다.")
        return 1

    if getattr(module, "RESULT_LABEL_HEIGHT", None) != 3:
        print("character ui smoke test 실패: 결과 문구 영역 높이가 예상과 다릅니다.")
        return 1

    if getattr(module, "NUDGE_EXAMPLE_LABEL", None) != "예시 입력":
        print("character ui smoke test 실패: Nudge 예시 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "CHECK_GROUP_LABEL", None) != "검증":
        print("character ui smoke test 실패: 검증 그룹 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "COMMAND_GROUP_LABEL", None) != "명령":
        print("character ui smoke test 실패: 명령 그룹 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "NUDGE_GROUP_LABEL", None) != "Nudge":
        print("character ui smoke test 실패: Nudge 그룹 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "PREVIEW_GROUP_LABEL", None) != "Preview 확인":
        print("character ui smoke test 실패: Preview 그룹 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "PREVIEW_HELP_LABEL", None) != "표시만 바뀜 · Refresh로 복귀":
        print("character ui smoke test 실패: Preview 안내 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "ALWAYS_ON_TOP_LABEL", None) != "항상 위":
        print("character ui smoke test 실패: 항상 위 토글 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "REFRESH_BUTTON_LABEL", None) != "Refresh":
        print("character ui smoke test 실패: 새로고침 버튼 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "CHECK_BUTTON_LABEL", None) != "Check":
        print("character ui smoke test 실패: Check 버튼 라벨이 예상과 다릅니다.")
        return 1

    expected_action_commands = {
        "Status": ["status"],
        "Review": ["review"],
        "Fast": ["prompt", "fast"],
        "Careful": ["prompt", "careful"],
    }
    if getattr(module, "ACTION_BUTTON_COMMANDS", None) != expected_action_commands:
        print("character ui smoke test 실패: 캐릭터 조작 버튼 명령이 예상과 다릅니다.")
        return 1

    if getattr(module, "NUDGE_BUTTON_LABEL", None) != "Nudge":
        print("character ui smoke test 실패: Nudge 버튼 라벨이 예상과 다릅니다.")
        return 1

    expected_nudge_examples = {
        "검증해줘": "검증해줘",
        "빨리": "빨리 해줘",
        "조심": "조심해서 해줘",
        "상태확인": "상태 어때",
    }
    if getattr(module, "NUDGE_EXAMPLES", None) != expected_nudge_examples:
        print("character ui smoke test 실패: Nudge 예시 입력 계약이 예상과 다릅니다.")
        return 1

    expected_nudge_reaction_rules = (
        (("빨리", "대충"), "(^.^)", "빠르게", "빠른 흐름으로 맞춰볼게요."),
        (("조심", "불안"), "(-.-)", "신중하게", "조심해서 살펴볼게요."),
        (("검증", "테스트", "되는지"), "(o_o)", "검증 준비", "검증 쪽으로 확인해볼게요."),
    )
    if getattr(module, "NUDGE_REACTION_RULES", None) != expected_nudge_reaction_rules:
        print("character ui smoke test 실패: Nudge 반응 규칙이 예상과 다릅니다.")
        return 1

    if getattr(module, "NUDGE_DEFAULT_REACTION", None) != ("(._.)", "해석 중", "무슨 뜻인지 살펴보고 있어요."):
        print("character ui smoke test 실패: Nudge 기본 반응이 예상과 다릅니다.")
        return 1

    if getattr(module, "NUDGE_REACTION_MESSAGE", None) != "Nudge 반응입니다. 결과가 오면 요약을 보여줍니다.":
        print("character ui smoke test 실패: Nudge 반응 안내 문구가 예상과 다릅니다.")
        return 1

    if getattr(module, "PREVIEW_STATES", None) != EXPECTED_PREVIEW_STATES:
        print("character ui smoke test 실패: 상태 프리뷰 버튼 계약이 예상과 다릅니다.")
        return 1

    if module.refresh_time_label("2026-05-16 14:32:10") != "마지막 갱신: 2026-05-16 14:32:10":
        print("character ui smoke test 실패: 갱신 시각 라벨이 예상과 다릅니다.")
        return 1

    if len(module.current_refresh_time()) != 19:
        print("character ui smoke test 실패: 갱신 시각 포맷 길이가 예상과 다릅니다.")
        return 1

    if module.build_state_command()[-2:] != ["harness_buddy.py", "state-json"]:
        print("character ui smoke test 실패: state-json 명령 생성이 예상과 다릅니다.")
        return 1

    if module.build_check_command()[-2:] != ["harness_buddy.py", "check"]:
        print("character ui smoke test 실패: check 명령 생성이 예상과 다릅니다.")
        return 1

    if module.build_cli_command(["status"])[-2:] != ["harness_buddy.py", "status"]:
        print("character ui smoke test 실패: 일반 CLI 명령 생성이 예상과 다릅니다.")
        return 1

    if module.running_action_message("Status") != "Status 실행 중...":
        print("character ui smoke test 실패: 조작 실행 중 메시지가 예상과 다릅니다.")
        return 1

    if module.completed_action_message("Status", 0) != "Status 완료":
        print("character ui smoke test 실패: 조작 성공 메시지가 예상과 다릅니다.")
        return 1

    if module.completed_action_message("Status", 1) != "Status 실패":
        print("character ui smoke test 실패: 조작 실패 메시지가 예상과 다릅니다.")
        return 1

    output_with_next_action = "\n".join(
        [
            "Codex Harness Buddy - status",
            "프로젝트: codex-harness-buddy",
            "현재 단계: 초기 세팅",
            "다음 행동: 필요하면 check 모드로 다시 검증",
        ]
    )
    if module.summarize_output(output_with_next_action) != "다음 행동: 필요하면 check 모드로 다시 검증":
        print("character ui smoke test 실패: 다음 행동 요약이 예상과 다릅니다.")
        return 1

    output_with_recommendation = "\n".join(
        [
            "Codex Harness Buddy - nudge",
            "입력: 검증해줘",
            "다음 명령: python tools/harness_buddy.py check",
        ]
    )
    if module.summarize_output(output_with_recommendation) != "다음 명령: python tools/harness_buddy.py check":
        print("character ui smoke test 실패: 다음 명령 요약이 예상과 다릅니다.")
        return 1

    output_with_mode = "\n".join(
        [
            "Codex Harness Buddy - fast",
            "운영 모드: 빠른 응답 우선",
            "다음 행동: 최소 CLI 하네스 설계",
        ]
    )
    if module.summarize_output(output_with_mode) != "운영 모드: 빠른 응답 우선":
        print("character ui smoke test 실패: 운영 모드 요약이 예상과 다릅니다.")
        return 1

    output_with_check_status = "\n".join(
        [
            "Codex Harness Buddy - review",
            "프로젝트: codex-harness-buddy",
            "마지막 검증: passed",
        ]
    )
    if module.summarize_output(output_with_check_status) != "마지막 검증: passed":
        print("character ui smoke test 실패: 마지막 검증 요약이 예상과 다릅니다.")
        return 1

    review_output = "\n".join(
        [
            "Codex Harness Buddy - review",
            "운영 모드: 완료 전 점검 우선",
            "마지막 검증: passed",
            "다음 행동: 변경 내용을 마무리 보고하거나 다음 하네스를 선택",
        ]
    )
    expected_review_summary = "\n".join(
        [
            "다음 행동: 변경 내용을 마무리 보고하거나 다음 하네스를 선택",
            "마지막 검증: passed",
        ]
    )
    if module.summarize_action_output("Review", review_output) != expected_review_summary:
        print("character ui smoke test 실패: Review 버튼 요약이 예상과 다릅니다.")
        return 1

    status_output = "\n".join(
        [
            "Codex Harness Buddy - status",
            "마지막 검증: passed",
            "검증 상태: 최신",
            "다음 행동: 필요하면 check 모드로 다시 검증",
        ]
    )
    expected_status_summary = "\n".join(
        [
            "마지막 검증: passed",
            "검증 상태: 최신",
        ]
    )
    if module.summarize_action_output("Status", status_output) != expected_status_summary:
        print("character ui smoke test 실패: Status 버튼 요약이 예상과 다릅니다.")
        return 1

    fast_prompt_output = "\n".join(
        [
            "[Codex Harness Buddy 지시문]",
            "이 세션에서는 fast 모드로 작업한다.",
            "짧게 판단하고, 필요한 최소 변경만 제안한다.",
        ]
    )
    expected_fast_summary = "\n".join(
        [
            "이 세션에서는 fast 모드로 작업한다.",
            "짧게 판단하고, 필요한 최소 변경만 제안한다.",
        ]
    )
    if module.summarize_action_output("Fast", fast_prompt_output) != expected_fast_summary:
        print("character ui smoke test 실패: Fast 버튼 요약이 예상과 다릅니다.")
        return 1

    nudge_output = "\n".join(
        [
            "Codex Harness Buddy - nudge",
            "감지된 의도: check",
            "다음 명령: python tools/harness_buddy.py check",
        ]
    )
    expected_nudge_summary = "\n".join(
        [
            "다음 명령: python tools/harness_buddy.py check",
            "감지된 의도: check",
        ]
    )
    if module.summarize_action_output("Nudge", nudge_output) != expected_nudge_summary:
        print("character ui smoke test 실패: Nudge 버튼 요약이 예상과 다릅니다.")
        return 1

    for state, expected_face in EXPECTED_FACES.items():
        if module.character_face(state) != expected_face:
            print("character ui smoke test 실패: 캐릭터 얼굴 매핑이 예상과 다릅니다.")
            print(f"- 상태: {state}")
            return 1

    if module.character_label("needs_review") != "점검 필요":
        print("character ui smoke test 실패: 캐릭터 라벨 매핑이 예상과 다릅니다.")
        return 1

    for state, expected_reaction in EXPECTED_REACTIONS.items():
        if module.character_reaction(state) != expected_reaction:
            print("character ui smoke test 실패: 캐릭터 반응 문구 매핑이 예상과 다릅니다.")
            print(f"- 상태: {state}")
            return 1

    sample_state = {
        "buddy": {
            "state": "ready",
            "message": "검증이 최신입니다.",
        }
    }
    view_model = module.build_character_view_model(sample_state)
    if view_model["face"] != "(^_^)" or view_model["label"] != "준비됨":
        print("character ui smoke test 실패: 캐릭터 표시 모델이 예상과 다릅니다.")
        return 1

    if view_model["reaction"] != "좋아요. 검증은 최신이에요.":
        print("character ui smoke test 실패: 캐릭터 표시 모델 반응 문구가 예상과 다릅니다.")
        return 1

    preview_model = module.build_preview_view_model("needs_review")
    if preview_model["label"] != "점검 필요" or preview_model["reaction"] != "점검이 필요해요. 실패 로그부터 볼게요.":
        print("character ui smoke test 실패: 상태 프리뷰 표시 모델이 예상과 다릅니다.")
        return 1

    if preview_model["message"] != "프리뷰 상태입니다. Refresh를 누르면 실제 상태로 돌아갑니다.":
        print("character ui smoke test 실패: 상태 프리뷰 안내 문구가 예상과 다릅니다.")
        return 1

    nudge_fast_model = module.build_nudge_reaction_view_model("빨리 해줘")
    if nudge_fast_model["label"] != "빠르게" or nudge_fast_model["face"] != "(^.^)":
        print("character ui smoke test 실패: 빠른 Nudge 반응 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_careful_model = module.build_nudge_reaction_view_model("조심해서 해줘")
    if nudge_careful_model["label"] != "신중하게" or nudge_careful_model["reaction"] != "조심해서 살펴볼게요.":
        print("character ui smoke test 실패: 신중 Nudge 반응 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_check_model = module.build_nudge_reaction_view_model("검증해줘")
    if nudge_check_model["label"] != "검증 준비" or nudge_check_model["reaction"] != "검증 쪽으로 확인해볼게요.":
        print("character ui smoke test 실패: 검증 Nudge 반응 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_default_model = module.build_nudge_reaction_view_model("뭐 하지")
    if nudge_default_model["label"] != "해석 중" or nudge_default_model["message"] != "Nudge 반응입니다. 결과가 오면 요약을 보여줍니다.":
        print("character ui smoke test 실패: 기본 Nudge 반응 표시 모델이 예상과 다릅니다.")
        return 1

    if not hasattr(module.CharacterApp, "refresh_state"):
        print("character ui smoke test 실패: CharacterApp.refresh_state 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "run_check"):
        print("character ui smoke test 실패: CharacterApp.run_check 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "set_check_enabled"):
        print("character ui smoke test 실패: CharacterApp.set_check_enabled 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "set_refresh_enabled"):
        print("character ui smoke test 실패: CharacterApp.set_refresh_enabled 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "set_action_enabled"):
        print("character ui smoke test 실패: CharacterApp.set_action_enabled 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "run_action"):
        print("character ui smoke test 실패: CharacterApp.run_action 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "run_nudge"):
        print("character ui smoke test 실패: CharacterApp.run_nudge 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "fill_nudge_example"):
        print("character ui smoke test 실패: CharacterApp.fill_nudge_example 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "preview_state"):
        print("character ui smoke test 실패: CharacterApp.preview_state 메서드가 없습니다.")
        return 1

    if getattr(module, "CHECK_RUNNING_MESSAGE", None) != "검증 실행 중...":
        print("character ui smoke test 실패: Check 실행 중 메시지가 예상과 다릅니다.")
        return 1

    if getattr(module, "CHECK_RUNNING_FACE", None) != "(o_o)":
        print("character ui smoke test 실패: Check 실행 중 얼굴이 예상과 다릅니다.")
        return 1

    if getattr(module, "CHECK_RUNNING_LABEL", None) != "검증 중":
        print("character ui smoke test 실패: Check 실행 중 라벨이 예상과 다릅니다.")
        return 1

    if getattr(module, "CHECK_RUNNING_REACTION", None) != "검증을 돌리고 있어요.":
        print("character ui smoke test 실패: Check 실행 중 반응 문구가 예상과 다릅니다.")
        return 1

    if getattr(module, "CHECK_RUNNING_STATUS_MESSAGE", None) != "잠시만 기다려 주세요.":
        print("character ui smoke test 실패: Check 실행 중 상태 메시지가 예상과 다릅니다.")
        return 1

    if getattr(module, "REACTION_MIN_DISPLAY_MS", None) != 800:
        print("character ui smoke test 실패: 반응 최소 표시 시간이 예상과 다릅니다.")
        return 1

    if module.remaining_display_ms(started_at_ms=1000, now_ms=1000) != 800:
        print("character ui smoke test 실패: 반응 표시 시작 직후 남은 시간이 예상과 다릅니다.")
        return 1

    if module.remaining_display_ms(started_at_ms=1000, now_ms=1500) != 300:
        print("character ui smoke test 실패: 반응 표시 중 남은 시간이 예상과 다릅니다.")
        return 1

    if module.remaining_display_ms(started_at_ms=1000, now_ms=1800) != 0:
        print("character ui smoke test 실패: 반응 최소 표시 시간이 지난 뒤 남은 시간이 예상과 다릅니다.")
        return 1

    if getattr(module, "CHECK_SUCCESS_MESSAGE", None) != "검증 성공. 상태를 갱신했습니다.":
        print("character ui smoke test 실패: Check 성공 메시지가 예상과 다릅니다.")
        return 1

    if getattr(module, "CHECK_FAILURE_MESSAGE", None) != "검증 실행에 실패했습니다.":
        print("character ui smoke test 실패: Check 실패 메시지가 예상과 다릅니다.")
        return 1

    if not hasattr(module.CharacterApp, "set_result_message"):
        print("character ui smoke test 실패: CharacterApp.set_result_message 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "apply_always_on_top"):
        print("character ui smoke test 실패: CharacterApp.apply_always_on_top 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "toggle_always_on_top"):
        print("character ui smoke test 실패: CharacterApp.toggle_always_on_top 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "start_check"):
        print("character ui smoke test 실패: CharacterApp.start_check 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "run_check_worker"):
        print("character ui smoke test 실패: CharacterApp.run_check_worker 메서드가 없습니다.")
        return 1

    if not hasattr(module.CharacterApp, "finish_check"):
        print("character ui smoke test 실패: CharacterApp.finish_check 메서드가 없습니다.")
        return 1

    check_running_model = module.build_check_running_view_model()
    expected_check_running_model = {
        "face": "(o_o)",
        "label": "검증 중",
        "reaction": "검증을 돌리고 있어요.",
        "message": "잠시만 기다려 주세요.",
    }
    if check_running_model != expected_check_running_model:
        print("character ui smoke test 실패: Check 실행 중 표시 모델이 예상과 다릅니다.")
        return 1

    print("character ui smoke test 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
