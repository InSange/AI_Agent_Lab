from pathlib import Path
from datetime import datetime
import json
import os
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PROJECT_ROOT / "tools" / "harness_buddy.py"
STATE_PATH = PROJECT_ROOT / "tmp" / f"smoke_buddy_state_{os.getpid()}.json"
APPROVAL_REQUIRED = "승인 필요: 파일/폴더 변경, 의존성/가상환경 변경, 모델/데이터 다운로드, Git 작업, 토큰/환경 변수 변경"

REQUIRED_OUTPUTS = [
    "Codex Harness Buddy",
    "프로젝트: codex-harness-buddy",
    "현재 단계: 초기 세팅",
    "다음 행동: 최소 CLI 하네스 설계",
    "검증 명령: python scripts/smoke_test.py",
]


def write_passed_state() -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "last_check": {
            "status": "passed",
            "command": "python scripts/check.py",
            "mode": "check",
            "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    }
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI_PATH), *args, "--state-path", str(STATE_PATH)],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def run_cli_with_env(extra_env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI_PATH), *args, "--state-path", str(STATE_PATH)],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", **extra_env},
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def check_normal_output() -> bool:
    result = run_cli()

    if result.returncode != 0:
        print("smoke test 실패: CLI가 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    missing = [text for text in REQUIRED_OUTPUTS if text not in output_lines]
    if missing:
        print("smoke test 실패: 필수 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_missing_harness_error() -> bool:
    result = run_cli("--harness-path", str(PROJECT_ROOT / "missing-HARNESS.md"))

    if result.returncode == 0:
        print("smoke test 실패: 없는 HARNESS.md 경로가 성공으로 처리되었습니다.")
        return False
    if "HARNESS.md를 찾지 못했습니다." not in result.stdout:
        print("smoke test 실패: 없는 HARNESS.md 오류 메시지가 누락되었습니다.")
        return False

    return True


def check_missing_required_item_error() -> bool:
    result = run_cli("--harness-path", str(PROJECT_ROOT / "README.md"))

    if result.returncode == 0:
        print("smoke test 실패: 필수 항목 누락이 성공으로 처리되었습니다.")
        return False
    if "HARNESS.md에서 필수 항목을 읽지 못했습니다." not in result.stdout:
        print("smoke test 실패: 필수 항목 누락 오류 메시지가 누락되었습니다.")
        return False

    return True


def check_mode_output(mode: str, required_outputs: list[str]) -> bool:
    result = run_cli(mode)

    if result.returncode != 0:
        print(f"smoke test 실패: {mode} 모드가 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    missing = [
        text
        for text in required_outputs
        if not any(line.startswith(text) for line in output_lines)
    ]
    if missing:
        print(f"smoke test 실패: {mode} 모드 필수 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_buddy_modes() -> bool:
    mode_checks = [
        (
            "fast",
            [
                "Codex Harness Buddy - fast",
                "운영 모드: 빠른 응답 우선",
                "트레이드오프: 속도를 우선하며 복잡한 판단의 검토 깊이는 줄어들 수 있음",
                "다음 행동: 최소 CLI 하네스 설계",
                "검증 명령: python scripts/smoke_test.py",
            ],
        ),
        (
            "careful",
            [
                "Codex Harness Buddy - careful",
                "운영 모드: 정확성과 승인 규칙 우선",
                "트레이드오프: 더 느릴 수 있지만 변경 전 위험과 검증을 더 분명히 확인함",
                "현재 단계: 초기 세팅",
                APPROVAL_REQUIRED,
                "검증 명령: python scripts/smoke_test.py",
            ],
        ),
        (
            "review",
            [
                "Codex Harness Buddy - review",
                "운영 모드: 완료 전 점검 우선",
                "트레이드오프: 새 구현보다 누락, 검증, 남은 이슈 확인에 집중함",
                "프로젝트: codex-harness-buddy",
                "현재 단계: 초기 세팅",
                "마지막 검증: passed",
                "마지막 검증 시각:",
                "다음 행동: 변경 내용을 마무리 보고하거나 다음 하네스를 선택",
            ],
        ),
    ]

    for mode, required_outputs in mode_checks:
        if not check_mode_output(mode, required_outputs):
            return False

    return True


def check_prompt_output(mode: str, required_outputs: list[str]) -> bool:
    result = run_cli("prompt", mode)

    if result.returncode != 0:
        print(f"smoke test 실패: prompt {mode} 명령이 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    missing = [text for text in required_outputs if text not in output_lines]
    if missing:
        print(f"smoke test 실패: prompt {mode} 필수 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_prompt_modes() -> bool:
    prompt_checks = [
        (
            "fast",
            [
                "[Codex Harness Buddy 지시문]",
                "이 세션에서는 fast 모드로 작업한다.",
                "짧게 판단하고, 필요한 최소 변경만 제안한다.",
                APPROVAL_REQUIRED,
                "복잡하거나 위험한 작업은 fast 모드라도 멈추고 확인한다.",
                "검증 명령은 python scripts/smoke_test.py를 우선 사용한다.",
            ],
        ),
        (
            "careful",
            [
                "[Codex Harness Buddy 지시문]",
                "이 세션에서는 careful 모드로 작업한다.",
                "변경 전 영향 파일, 이유, 검증 방법을 먼저 정리한다.",
                APPROVAL_REQUIRED,
                "검증 명령은 python scripts/smoke_test.py를 우선 사용한다.",
            ],
        ),
        (
            "review",
            [
                "[Codex Harness Buddy 지시문]",
                "이 세션에서는 review 모드로 작업한다.",
                "새 구현보다 누락, 검증 결과, 남은 위험을 먼저 확인한다.",
                "검증 명령은 python scripts/smoke_test.py를 우선 사용한다.",
            ],
        ),
    ]

    for mode, required_outputs in prompt_checks:
        if not check_prompt_output(mode, required_outputs):
            return False

    return True


def check_help_command() -> bool:
    result = run_cli("help")

    if result.returncode != 0:
        print("smoke test 실패: help 명령이 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    required_outputs = [
        "Codex Harness Buddy - help",
        "자주 쓰는 명령",
        "- python tools/harness_buddy.py",
        "  현재 프로젝트 요약 출력",
        "- python tools/harness_buddy.py check",
        "  전체 자동 검증 실행",
        "- python tools/harness_buddy.py nudge \"검증해줘\"",
        "  키워드 규칙으로 의도 추천",
        "- python tools/harness_buddy.py evaluate-nudge",
        "  nudge 분류 평가 실행",
        "- python tools/harness_buddy.py state-json",
        "  캐릭터 UI용 상태 JSON 출력",
        "- python tools/harness_buddy.py manual-check",
        "  캐릭터 UI 수동 확인 안내",
        "프로젝트 폴더에서:",
        "python tools/harness_buddy.py check",
        "python tools/harness_buddy.py evaluate-nudge",
        "python tools/harness_buddy.py state-json",
        "python tools/harness_buddy.py manual-check",
        "python scripts/check.py",
        "루트 폴더에서:",
        "python codex-harness-buddy\\tools\\harness_buddy.py check",
        "python codex-harness-buddy\\tools\\harness_buddy.py evaluate-nudge",
        "python codex-harness-buddy\\tools\\harness_buddy.py state-json",
        "python codex-harness-buddy\\tools\\harness_buddy.py manual-check",
        "python codex-harness-buddy\\scripts\\check.py",
        "보통은 이것부터 실행:",
        "프로젝트 폴더: python scripts/check.py",
        "루트 폴더: python codex-harness-buddy\\scripts\\check.py",
    ]
    missing = [text for text in required_outputs if text not in output_lines]
    if missing:
        print("smoke test 실패: help 명령 필수 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_manual_check_command() -> bool:
    result = run_cli("manual-check")

    if result.returncode != 0:
        print("smoke test 실패: manual-check 명령이 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    required_outputs = [
        "Codex Harness Buddy - manual-check",
        "캐릭터 UI 실행:",
        "프로젝트 폴더: python tools/buddy_character.py",
        "루트 폴더: python codex-harness-buddy\\tools\\buddy_character.py",
        "Nudge 확인:",
        "- 빨리 해줘 -> 빠르게",
        "- 조심해서 해줘 -> 신중하게",
        "- 검증해줘 -> 검증 준비",
        "Check 확인:",
        "- Check 클릭 시 검증 중 라벨이 최소 0.8초 보이는지",
        "Preview 확인:",
        "- Waiting/Needs Review 버튼 후 Refresh로 실제 상태에 돌아오는지",
    ]
    missing = [text for text in required_outputs if text not in output_lines]
    if missing:
        print("smoke test 실패: manual-check 명령 필수 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_buddy_check_command() -> bool:
    if os.environ.get("HARNESS_BUDDY_SKIP_CHECK_COMMAND_TEST") == "1":
        return True

    result = run_cli("check")

    if result.returncode != 0:
        print("smoke test 실패: check 명령이 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    required_outputs = [
        "Codex Harness Buddy - check",
        "검증 실행: python scripts/check.py",
        "검증 요약",
        "- CLI: 기본 실행과 HARNESS 읽기 확인",
        "- smoke test: 모드, 상태 파일, nudge 규칙 확인",
        "- UI smoke test: 버튼 계약과 UI 헬퍼 확인",
        "- character UI smoke test: 캐릭터 창 상태 표시와 조작 버튼 계약 확인",
        "- nudge 평가: 별도 실행 대상",
        "선택 검증",
        "프로젝트 폴더:",
        "- nudge 평가: python tools/harness_buddy.py evaluate-nudge",
        "- 캐릭터 UI 수동 확인: python tools/buddy_character.py",
        "- UI 수동 확인: python tools/buddy_ui.py",
        "루트 폴더:",
        "- nudge 평가: python codex-harness-buddy\\tools\\harness_buddy.py evaluate-nudge",
        "- 캐릭터 UI 수동 확인: python codex-harness-buddy\\tools\\buddy_character.py",
        "- UI 수동 확인: python codex-harness-buddy\\tools\\buddy_ui.py",
        "다음 확인: 캐릭터 창은 필요 시 직접 실행해 버튼과 상태 표시를 확인",
        "수동 확인:",
        "[레이아웃]",
        "- 캐릭터 UI: Review 후 Nudge 입력창이 보이는지",
        "- 캐릭터 UI: 예시 입력 버튼이 의미 있게 보이는지",
        "[상호작용]",
        "- 캐릭터 UI: Check 실행 중 얼굴과 라벨이 검증 중으로 바뀌는지",
        "- 캐릭터 UI: 예시 입력 후 Nudge 실행 결과가 표시되는지",
        "- 캐릭터 UI: Nudge 입력에 따라 빠르게/신중하게/검증 준비 라벨이 바뀌는지",
        "- 캐릭터 UI: Nudge/Check 반응 라벨이 너무 빨리 사라지지 않는지",
        "- 캐릭터 UI: 항상 위 체크/해제 시 창 z축 동작이 바뀌는지",
        "[Preview]",
        "- 캐릭터 UI: Waiting/Needs Review 프리뷰에서 얼굴, 라벨, 반응 문구가 바뀌는지",
        "- 캐릭터 UI: Preview 확인 후 Refresh로 실제 상태에 돌아오는지",
        "- 캐릭터 UI: Preview 안내 문구가 표시 변경과 Refresh 복귀를 이해시키는지",
        "전체 검증 성공",
        "다음 행동: 결과를 확인하고 필요하면 review 모드로 점검",
    ]
    missing = [text for text in required_outputs if text not in output_lines]
    if missing:
        print("smoke test 실패: check 명령 필수 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    if not STATE_PATH.exists():
        print("smoke test 실패: check 명령 후 buddy_state.json이 생성되지 않았습니다.")
        return False

    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    last_check = state.get("last_check", {})
    expected_state = {
        "status": "passed",
        "command": "python scripts/check.py",
        "mode": "check",
    }
    for key, expected_value in expected_state.items():
        if last_check.get(key) != expected_value:
            print(f"smoke test 실패: last_check.{key} 값이 예상과 다릅니다.")
            print(f"- 기대: {expected_value}")
            print(f"- 실제: {last_check.get(key)}")
            return False
    if "checked_at" not in last_check:
        print("smoke test 실패: last_check.checked_at 값이 누락되었습니다.")
        return False

    return True


def check_evaluate_nudge_command() -> bool:
    result = run_cli("evaluate-nudge")

    if result.returncode != 0:
        print("smoke test 실패: evaluate-nudge 명령이 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    required_outputs = [
        "Codex Harness Buddy - evaluate-nudge",
        "평가 실행: python scripts/evaluate_nudge.py",
        "Nudge 분류 평가",
        "분류기: rules",
        "분류 방식: 키워드 규칙",
        "모델 사용: 없음",
        "정확도: 10/10",
    ]
    missing = [text for text in required_outputs if text not in output_lines]
    if missing:
        print("smoke test 실패: evaluate-nudge 명령 필수 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_status_command() -> bool:
    if os.environ.get("HARNESS_BUDDY_SKIP_CHECK_COMMAND_TEST") == "1":
        return True

    result = run_cli("status")

    if result.returncode != 0:
        print("smoke test 실패: status 명령이 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    required_outputs = [
        "Codex Harness Buddy - status",
        "프로젝트: codex-harness-buddy",
        "현재 단계: 초기 세팅",
        "마지막 검증: passed",
        "마지막 검증 시각:",
        "검증 명령: python scripts/check.py",
        "다음 행동: 필요하면 check 모드로 다시 검증",
    ]
    missing = [
        text
        for text in required_outputs
        if not any(line.startswith(text) for line in output_lines)
    ]
    if missing:
        print("smoke test 실패: status 명령 필수 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_state_json_command() -> bool:
    result = run_cli("state-json")

    if result.returncode != 0:
        print("smoke test 실패: state-json 명령이 0이 아닌 종료 코드를 반환했습니다.")
        print(result.stderr.strip())
        return False

    try:
        state = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print("smoke test 실패: state-json 출력이 JSON이 아닙니다.")
        print(str(exc))
        return False

    if state.get("project") != "codex-harness-buddy":
        print("smoke test 실패: state-json project 값이 예상과 다릅니다.")
        return False
    if state.get("stage") != "초기 세팅":
        print("smoke test 실패: state-json stage 값이 예상과 다릅니다.")
        return False
    if state.get("last_check", {}).get("status") != "passed":
        print("smoke test 실패: state-json last_check.status 값이 예상과 다릅니다.")
        return False
    if state.get("buddy", {}).get("state") not in ["ready", "stale", "waiting", "needs_review"]:
        print("smoke test 실패: state-json buddy.state 값이 예상 범위가 아닙니다.")
        return False
    if "message" not in state.get("buddy", {}):
        print("smoke test 실패: state-json buddy.message 값이 누락되었습니다.")
        return False

    return True


def check_failed_check_summary() -> bool:
    if os.environ.get("HARNESS_BUDDY_SKIP_CHECK_COMMAND_TEST") == "1":
        return True

    result = run_cli_with_env({"HARNESS_BUDDY_FORCE_CHECK_FAILURE": "1"}, "check")

    if result.returncode == 0:
        print("smoke test 실패: 강제 실패 check 명령이 성공으로 처리되었습니다.")
        return False

    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    last_check = state.get("last_check", {})
    if last_check.get("status") != "failed":
        print("smoke test 실패: 실패 check 결과가 failed로 저장되지 않았습니다.")
        return False
    if last_check.get("summary") != "강제 실패: smoke test 실패 예시":
        print("smoke test 실패: 실패 요약이 예상과 다릅니다.")
        print(f"- 실제: {last_check.get('summary')}")
        return False

    status_result = run_cli("status")
    if "실패 요약: 강제 실패: smoke test 실패 예시" not in status_result.stdout:
        print("smoke test 실패: status 출력에 실패 요약이 없습니다.")
        return False

    review_result = run_cli("review")
    required_review_outputs = [
        "마지막 검증: failed",
        "실패 요약: 강제 실패: smoke test 실패 예시",
        "검증 명령: python scripts/check.py",
        "다음 행동:",
        "1. 실패 명령을 다시 실행한다.",
        "2. 실패 로그의 핵심 줄을 확인한다.",
        "3. 최소 수정만 적용한다.",
        "4. 같은 검증 명령을 다시 실행한다.",
    ]
    missing = [
        text
        for text in required_review_outputs
        if not any(line.startswith(text) for line in review_result.stdout.splitlines())
    ]
    if missing:
        print("smoke test 실패: 실패 상태 review 출력이 누락되었습니다.")
        for text in missing:
            print(f"- {text}")
        return False

    write_passed_state()

    return True


def check_stale_state_warning() -> bool:
    if os.environ.get("HARNESS_BUDDY_SKIP_CHECK_COMMAND_TEST") == "1":
        return True

    old_state = {
        "last_check": {
            "status": "passed",
            "command": "python scripts/check.py",
            "mode": "check",
            "checked_at": "2000-01-01T00:00:00+09:00",
        }
    }
    STATE_PATH.write_text(
        json.dumps(old_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    status_result = run_cli("status")
    status_required = [
        "검증 상태: 오래됨",
        "다음 행동: python tools/harness_buddy.py check",
    ]
    status_missing = [
        text
        for text in status_required
        if not any(line.startswith(text) for line in status_result.stdout.splitlines())
    ]
    if status_missing:
        print("smoke test 실패: status 오래된 검증 안내가 누락되었습니다.")
        for text in status_missing:
            print(f"- {text}")
        return False

    review_result = run_cli("review")
    review_required = [
        "검증 상태: 오래됨",
        "다음 행동: 먼저 check 모드로 다시 검증",
    ]
    review_missing = [
        text
        for text in review_required
        if not any(line.startswith(text) for line in review_result.stdout.splitlines())
    ]
    if review_missing:
        print("smoke test 실패: review 오래된 검증 안내가 누락되었습니다.")
        for text in review_missing:
            print(f"- {text}")
        return False

    write_passed_state()
    return True


def check_nudge_output(user_input: str, intent: str, reason: str, next_command: str) -> bool:
    result = run_cli("nudge", user_input)

    if result.returncode != 0:
        print(f"smoke test 실패: nudge 입력이 0이 아닌 종료 코드를 반환했습니다: {user_input}")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    required_outputs = [
        "Codex Harness Buddy - nudge",
        f"입력: {user_input}",
        "분류 방식: 키워드 규칙",
        "모델 사용: 없음",
        "실행 여부: 추천만 함",
        f"감지된 의도: {intent}",
        f"이유: {reason}",
        f"다음 명령: {next_command}",
    ]
    missing = [text for text in required_outputs if text not in output_lines]
    if missing:
        print(f"smoke test 실패: nudge 출력이 누락되었습니다: {user_input}")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_nudge_contains(user_input: str, required_outputs: list[str]) -> bool:
    result = run_cli("nudge", user_input)

    if result.returncode != 0:
        print(f"smoke test 실패: nudge 입력이 0이 아닌 종료 코드를 반환했습니다: {user_input}")
        print(result.stderr.strip())
        return False

    output_lines = result.stdout.splitlines()
    missing = [
        text
        for text in required_outputs
        if not any(line.startswith(text) for line in output_lines)
    ]
    if missing:
        print(f"smoke test 실패: 상태 기반 nudge 출력이 누락되었습니다: {user_input}")
        for text in missing:
            print(f"- {text}")
        return False

    return True


def check_nudge_modes() -> bool:
    if os.environ.get("HARNESS_BUDDY_SKIP_CHECK_COMMAND_TEST") == "1":
        return True

    import importlib.util

    spec = importlib.util.spec_from_file_location("harness_buddy", CLI_PATH)
    if spec is None or spec.loader is None:
        print("smoke test 실패: harness_buddy.py를 import할 수 없습니다.")
        return False
    module = importlib.util.module_from_spec(spec)
    sys.modules["harness_buddy"] = module
    spec.loader.exec_module(module)

    classification = module.classify_nudge("검증해줘")
    if classification.intent != "check":
        print("smoke test 실패: nudge 분류 결과 객체의 intent가 예상과 다릅니다.")
        return False
    if classification.method != "키워드 규칙":
        print("smoke test 실패: nudge 분류 방식 메타데이터가 예상과 다릅니다.")
        return False
    if classification.uses_model:
        print("smoke test 실패: 규칙 기반 nudge가 모델 사용으로 표시되었습니다.")
        return False

    nudge_checks = [
        ("빨리 좀 해", "fast", "빠른 진행 요청으로 보임", "python tools/harness_buddy.py prompt fast"),
        ("대충 빨리 가자", "fast", "빠른 진행 요청으로 보임", "python tools/harness_buddy.py prompt fast"),
        ("조심해서 해", "careful", "신중한 작업 요청으로 보임", "python tools/harness_buddy.py prompt careful"),
        ("좀 불안한데", "careful", "신중한 작업 요청으로 보임", "python tools/harness_buddy.py prompt careful"),
        ("끝났어?", "review", "완료 여부 확인 요청으로 보임", "python tools/harness_buddy.py review"),
        ("이거 믿어도 돼?", "review", "완료 여부 확인 요청으로 보임", "python tools/harness_buddy.py review"),
        ("마무리해도 돼?", "review", "완료 여부 확인 요청으로 보임", "python tools/harness_buddy.py review"),
        ("검증해줘", "check", "검증 실행 요청으로 보임", "python tools/harness_buddy.py check"),
        ("일단 되는지만 봐", "check", "검증 실행 요청으로 보임", "python tools/harness_buddy.py check"),
        ("테스트 돌려", "check", "검증 실행 요청으로 보임", "python tools/harness_buddy.py check"),
        ("상태 보여줘", "status", "상태 확인 요청으로 보임", "python tools/harness_buddy.py status"),
        ("지금 상태 어때", "status", "상태 확인 요청으로 보임", "python tools/harness_buddy.py status"),
    ]

    for user_input, intent, reason, next_command in nudge_checks:
        if not check_nudge_output(user_input, intent, reason, next_command):
            return False

    write_passed_state()
    if not check_nudge_contains(
        "끝났어?",
        [
            "분류 방식: 키워드 규칙",
            "모델 사용: 없음",
            "실행 여부: 추천만 함",
            "감지된 의도: review",
            "현재 검증 상태: 최신",
            "추천 행동: review로 완료 전 점검",
            "다음 명령: python tools/harness_buddy.py review",
        ],
    ):
        return False

    old_state = {
        "last_check": {
            "status": "passed",
            "command": "python scripts/check.py",
            "mode": "check",
            "checked_at": "2000-01-01T00:00:00+09:00",
        }
    }
    STATE_PATH.write_text(
        json.dumps(old_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not check_nudge_contains(
        "끝났어?",
        [
            "분류 방식: 키워드 규칙",
            "모델 사용: 없음",
            "실행 여부: 추천만 함",
            "감지된 의도: review",
            "현재 검증 상태: 오래됨",
            "추천 행동: 먼저 check 실행",
            "다음 명령: python tools/harness_buddy.py check",
        ],
    ):
        return False

    failed_state = {
        "last_check": {
            "status": "failed",
            "command": "python scripts/check.py",
            "mode": "check",
            "checked_at": "smoke-test",
            "summary": "강제 실패: smoke test 실패 예시",
        }
    }
    STATE_PATH.write_text(
        json.dumps(failed_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not check_nudge_contains(
        "끝났어?",
        [
            "분류 방식: 키워드 규칙",
            "모델 사용: 없음",
            "실행 여부: 추천만 함",
            "감지된 의도: review",
            "현재 검증 상태: failed",
            "실패 요약: 강제 실패: smoke test 실패 예시",
            "추천 행동: review로 실패 원인 점검",
            "다음 명령: python tools/harness_buddy.py review",
        ],
    ):
        return False

    write_passed_state()
    return True


def main() -> int:
    write_passed_state()

    checks = [
        check_normal_output,
        check_missing_harness_error,
        check_missing_required_item_error,
        check_buddy_modes,
        check_prompt_modes,
        check_help_command,
        check_manual_check_command,
        check_buddy_check_command,
        check_evaluate_nudge_command,
        check_status_command,
        check_state_json_command,
        check_failed_check_summary,
        check_stale_state_warning,
        check_nudge_modes,
    ]

    for check in checks:
        if not check():
            return 1

    print("smoke test 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
