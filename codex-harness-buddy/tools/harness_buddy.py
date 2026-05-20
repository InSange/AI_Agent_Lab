import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = PROJECT_ROOT / "HARNESS.md"
NEXT_ACTION = "최소 CLI 하네스 설계"
REMAINING_ISSUES = "승인 체크리스트 출력, 상태 파일 저장은 이후 단계에서 구현"
APPROVAL_REQUIRED = "승인 필요: 파일/폴더 변경, 의존성/가상환경 변경, 모델/데이터 다운로드, Git 작업, 토큰/환경 변수 변경"
MODES = ["fast", "careful", "review"]
COMMANDS = [*MODES, "check", "status", "prompt", "nudge", "evaluate-nudge", "state-json", "manual-check", "character", "help"]
CHECK_PATH = PROJECT_ROOT / "scripts" / "check.py"
EVALUATE_NUDGE_PATH = PROJECT_ROOT / "scripts" / "evaluate_nudge.py"
CHARACTER_PATH = PROJECT_ROOT / "tools" / "buddy_character.py"
STATE_PATH = PROJECT_ROOT / "buddy_state.json"
STALE_AFTER = timedelta(minutes=30)


@dataclass(frozen=True)
class NudgeClassification:
    intent: str
    reason: str
    next_command: str
    method: str = "키워드 규칙"
    uses_model: bool = False


def read_code_block_after_heading(text: str, heading: str) -> str | None:
    lines = text.splitlines()

    for index, line in enumerate(lines):
        if line.strip() != heading:
            continue

        in_block = False
        values: list[str] = []
        for next_line in lines[index + 1 :]:
            stripped = next_line.strip()
            if stripped.startswith("```"):
                if in_block:
                    return "\n".join(values).strip()
                in_block = True
                continue
            if in_block:
                values.append(next_line)

    return None


REQUIRED_FIELDS = [
    ("프로젝트 이름", "### 프로젝트 이름"),
    ("현재 단계", "### 현재 단계"),
    ("스모크 테스트", "### 스모크 테스트"),
]


def load_harness_values(harness_path: Path) -> dict[str, str]:
    harness_text = harness_path.read_text(encoding="utf-8")
    project_name = read_code_block_after_heading(harness_text, "### 프로젝트 이름")
    current_stage = read_code_block_after_heading(harness_text, "### 현재 단계")
    smoke_command = read_code_block_after_heading(harness_text, "### 스모크 테스트")

    return {
        "project_name": project_name or "",
        "current_stage": current_stage or "",
        "smoke_command": smoke_command or "",
    }


def load_summary(harness_path: Path) -> list[str]:
    values = load_harness_values(harness_path)

    return [
        "Codex Harness Buddy",
        f"프로젝트: {values['project_name']}",
        f"현재 단계: {values['current_stage']}",
        f"다음 행동: {NEXT_ACTION}",
        f"검증 명령: {values['smoke_command']}",
    ]


def load_help_summary() -> list[str]:
    return [
        "Codex Harness Buddy - help",
        "",
        "자주 쓰는 명령",
        "- python tools/harness_buddy.py",
        "  현재 프로젝트 요약 출력",
        "- python tools/harness_buddy.py check",
        "  전체 자동 검증 실행",
        "- python tools/harness_buddy.py status",
        "  마지막 검증 상태 확인",
        "- python tools/harness_buddy.py nudge \"검증해줘\"",
        "  키워드 규칙으로 의도 추천",
        "- python tools/harness_buddy.py evaluate-nudge",
        "  nudge 분류 평가 실행",
        "- python tools/harness_buddy.py state-json",
        "  캐릭터 UI용 상태 JSON 출력",
        "- python tools/harness_buddy.py manual-check",
        "  캐릭터 UI 수동 확인 안내",
        "- python tools/harness_buddy.py character --character-only",
        "  캐릭터 중심 UI 실행",
        "",
        "프로젝트 폴더에서:",
        "python tools/harness_buddy.py check",
        "python tools/harness_buddy.py evaluate-nudge",
        "python tools/harness_buddy.py state-json",
        "python tools/harness_buddy.py manual-check",
        "python tools/harness_buddy.py character --character-only",
        "python scripts/check.py",
        "",
        "루트 폴더에서:",
        "python codex-harness-buddy\\tools\\harness_buddy.py check",
        "python codex-harness-buddy\\tools\\harness_buddy.py evaluate-nudge",
        "python codex-harness-buddy\\tools\\harness_buddy.py state-json",
        "python codex-harness-buddy\\tools\\harness_buddy.py manual-check",
        "python codex-harness-buddy\\tools\\harness_buddy.py character --character-only",
        "python codex-harness-buddy\\scripts\\check.py",
        "",
        "보통은 이것부터 실행:",
        "프로젝트 폴더: python scripts/check.py",
        "루트 폴더: python codex-harness-buddy\\scripts\\check.py",
    ]


def load_manual_check_summary() -> list[str]:
    return [
        "Codex Harness Buddy - manual-check",
        "",
        "캐릭터 UI 실행:",
        "프로젝트 폴더: python tools/buddy_character.py",
        "루트 폴더: python codex-harness-buddy\\tools\\buddy_character.py",
        "",
        "Nudge 확인:",
        "- 빨리 해줘 -> 빠르게",
        "- 조심해서 해줘 -> 신중하게",
        "- 검증해줘 -> 검증 준비",
        "",
        "Check 확인:",
        "- Check 클릭 시 검증 중 라벨이 최소 0.8초 보이는지",
        "",
        "Preview 확인:",
        "- Waiting/Needs Review 버튼 후 Refresh로 실제 상태에 돌아오는지",
    ]


def build_character_command(character_only: bool = False) -> list[str]:
    command = [sys.executable, str(CHARACTER_PATH)]
    if character_only:
        command.append("--character-only")
    return command


def run_character_ui(character_only: bool = False) -> int:
    return subprocess.run(build_character_command(character_only)).returncode


def get_freshness_label(checked_at: str | None) -> str:
    if not checked_at:
        return "알 수 없음"
    try:
        checked_time = datetime.fromisoformat(checked_at)
    except ValueError:
        return "알 수 없음"
    if checked_time.tzinfo is None:
        checked_time = checked_time.astimezone()

    now = datetime.now().astimezone()
    if now - checked_time > STALE_AFTER:
        return "오래됨"
    return "최신"


def load_mode_summary(harness_path: Path, mode: str, state_path: Path) -> list[str]:
    values = load_harness_values(harness_path)

    if mode == "fast":
        return [
            "Codex Harness Buddy - fast",
            "운영 모드: 빠른 응답 우선",
            "트레이드오프: 속도를 우선하며 복잡한 판단의 검토 깊이는 줄어들 수 있음",
            f"다음 행동: {NEXT_ACTION}",
            f"검증 명령: {values['smoke_command']}",
        ]

    if mode == "careful":
        return [
            "Codex Harness Buddy - careful",
            "운영 모드: 정확성과 승인 규칙 우선",
            "트레이드오프: 더 느릴 수 있지만 변경 전 위험과 검증을 더 분명히 확인함",
            f"현재 단계: {values['current_stage']}",
            APPROVAL_REQUIRED,
            f"검증 명령: {values['smoke_command']}",
        ]

    if mode == "review":
        lines = [
            "Codex Harness Buddy - review",
            "운영 모드: 완료 전 점검 우선",
            "트레이드오프: 새 구현보다 누락, 검증, 남은 이슈 확인에 집중함",
            f"프로젝트: {values['project_name']}",
            f"현재 단계: {values['current_stage']}",
        ]
        if not state_path.exists():
            return [
                *lines,
                "마지막 검증 기록이 없습니다.",
                "다음 행동: python tools/harness_buddy.py check",
            ]

        state = json.loads(state_path.read_text(encoding="utf-8"))
        last_check = state.get("last_check", {})
        freshness = get_freshness_label(last_check.get("checked_at"))
        lines.extend(
            [
                f"마지막 검증: {last_check.get('status', 'unknown')}",
                f"마지막 검증 시각: {last_check.get('checked_at', 'unknown')}",
                f"검증 상태: {freshness}",
            ]
        )
        if last_check.get("status") == "failed" and last_check.get("summary"):
            lines.extend(
                [
                    f"실패 요약: {last_check['summary']}",
                    f"검증 명령: {last_check.get('command', 'python scripts/check.py')}",
                    "다음 행동:",
                    "1. 실패 명령을 다시 실행한다.",
                    "2. 실패 로그의 핵심 줄을 확인한다.",
                    "3. 최소 수정만 적용한다.",
                    "4. 같은 검증 명령을 다시 실행한다.",
                ]
            )
        elif freshness == "오래됨":
            lines.append("다음 행동: 먼저 check 모드로 다시 검증")
        else:
            lines.append("다음 행동: 변경 내용을 마무리 보고하거나 다음 하네스를 선택")
        return lines

    return load_summary(harness_path)


def load_prompt(mode: str, smoke_command: str) -> list[str]:
    common_lines = [
        "[Codex Harness Buddy 지시문]",
        f"이 세션에서는 {mode} 모드로 작업한다.",
    ]

    if mode == "fast":
        mode_lines = [
            "짧게 판단하고, 필요한 최소 변경만 제안한다.",
            APPROVAL_REQUIRED,
            "복잡하거나 위험한 작업은 fast 모드라도 멈추고 확인한다.",
        ]
    elif mode == "careful":
        mode_lines = [
            "변경 전 영향 파일, 이유, 검증 방법을 먼저 정리한다.",
            APPROVAL_REQUIRED,
        ]
    else:
        mode_lines = [
            "새 구현보다 누락, 검증 결과, 남은 위험을 먼저 확인한다.",
        ]

    return [
        *common_lines,
        *mode_lines,
        f"검증 명령은 {smoke_command}를 우선 사용한다.",
    ]


def classify_nudge_with_rules(user_input: str) -> NudgeClassification:
    lowered = user_input.lower()
    rules = [
        ("check", ["검증", "테스트", "check", "돌려", "되는지", "되는지만"], "검증 실행 요청으로 보임", "python tools/harness_buddy.py check"),
        ("careful", ["조심", "꼼꼼", "위험", "승인", "careful", "불안", "천천히"], "신중한 작업 요청으로 보임", "python tools/harness_buddy.py prompt careful"),
        ("review", ["끝", "확인", "리뷰", "review", "됐어", "믿어도", "마무리"], "완료 여부 확인 요청으로 보임", "python tools/harness_buddy.py review"),
        ("status", ["상태", "status", "어때", "현재"], "상태 확인 요청으로 보임", "python tools/harness_buddy.py status"),
        ("fast", ["빨리", "급해", "재촉", "닦달", "fast", "대충", "후딱"], "빠른 진행 요청으로 보임", "python tools/harness_buddy.py prompt fast"),
    ]

    for intent, keywords, reason, next_command in rules:
        if any(keyword in lowered for keyword in keywords):
            return NudgeClassification(intent=intent, reason=reason, next_command=next_command)

    return NudgeClassification(
        intent="review",
        reason="명확한 의도를 찾지 못해 점검 요청으로 처리함",
        next_command="python tools/harness_buddy.py review",
    )


def classify_nudge(user_input: str) -> NudgeClassification:
    return classify_nudge_with_rules(user_input)


def load_nudge_summary(user_input: str, state_path: Path) -> list[str]:
    classification = classify_nudge(user_input)
    lines = [
        "Codex Harness Buddy - nudge",
        f"입력: {user_input}",
        f"분류 방식: {classification.method}",
        f"모델 사용: {'사용' if classification.uses_model else '없음'}",
        "실행 여부: 추천만 함",
        f"감지된 의도: {classification.intent}",
        f"이유: {classification.reason}",
    ]

    if classification.intent == "review" and state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        last_check = state.get("last_check", {})
        if last_check.get("status") == "failed":
            lines.extend(
                [
                    "현재 검증 상태: failed",
                    f"실패 요약: {last_check.get('summary', '요약 없음')}",
                    "추천 행동: review로 실패 원인 점검",
                    "다음 명령: python tools/harness_buddy.py review",
                ]
            )
            return lines

        freshness = get_freshness_label(last_check.get("checked_at"))
        lines.append(f"현재 검증 상태: {freshness}")
        if freshness == "오래됨":
            lines.extend(
                [
                    "추천 행동: 먼저 check 실행",
                    "다음 명령: python tools/harness_buddy.py check",
                ]
            )
        else:
            lines.extend(
                [
                    "추천 행동: review로 완료 전 점검",
                    "다음 명령: python tools/harness_buddy.py review",
                ]
            )
        return lines

    lines.append(f"다음 명령: {classification.next_command}")
    return lines


def extract_failure_summary(result: subprocess.CompletedProcess[str]) -> str:
    combined_output = "\n".join([result.stdout, result.stderr])
    for line in combined_output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "실패" in stripped or "[FAIL]" in stripped:
            return stripped
    return "검증 실패 원인을 요약하지 못했습니다."


def write_last_check_state(state_path: Path, status: str, summary: str | None = None) -> None:
    last_check = {
        "status": status,
        "command": "python scripts/check.py",
        "mode": "check",
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if summary:
        last_check["summary"] = summary

    state = {"last_check": last_check}
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_project_check(state_path: Path) -> int:
    print("Codex Harness Buddy - check")
    print("검증 실행: python scripts/check.py")

    result = subprocess.run(
        [sys.executable, str(CHECK_PATH)],
        cwd=PROJECT_ROOT,
        env={
            **os.environ,
            "PYTHONIOENCODING": "utf-8",
            "HARNESS_BUDDY_SKIP_CHECK_COMMAND_TEST": "1",
        },
        text=True,
        encoding="utf-8",
        capture_output=True,
    )

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())

    if result.returncode != 0:
        write_last_check_state(state_path, "failed", extract_failure_summary(result))
        print("전체 검증 실패")
        print("다음 행동: 실패 로그를 확인하고 review 모드로 원인을 점검")
        return 1

    write_last_check_state(state_path, "passed")
    print("다음 행동: 결과를 확인하고 필요하면 review 모드로 점검")
    return 0


def run_nudge_evaluation() -> int:
    print("Codex Harness Buddy - evaluate-nudge")
    print("평가 실행: python scripts/evaluate_nudge.py")

    result = subprocess.run(
        [sys.executable, str(EVALUATE_NUDGE_PATH)],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        text=True,
        encoding="utf-8",
        capture_output=True,
    )

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())

    return result.returncode


def load_status_summary(harness_path: Path, state_path: Path) -> list[str]:
    values = load_harness_values(harness_path)

    if not state_path.exists():
        return [
            "Codex Harness Buddy - status",
            "마지막 검증 기록이 없습니다.",
            "다음 행동: python tools/harness_buddy.py check",
        ]

    state = json.loads(state_path.read_text(encoding="utf-8"))
    last_check = state.get("last_check", {})
    freshness = get_freshness_label(last_check.get("checked_at"))

    lines = [
        "Codex Harness Buddy - status",
        f"프로젝트: {values['project_name']}",
        f"현재 단계: {values['current_stage']}",
        f"마지막 검증: {last_check.get('status', 'unknown')}",
        f"마지막 검증 시각: {last_check.get('checked_at', 'unknown')}",
        f"검증 상태: {freshness}",
        f"검증 명령: {last_check.get('command', 'python scripts/check.py')}",
    ]
    if last_check.get("status") == "failed" and last_check.get("summary"):
        lines.append(f"실패 요약: {last_check['summary']}")
        lines.append("다음 행동: review 모드로 실패 원인을 점검")
    elif freshness == "오래됨":
        lines.append("다음 행동: python tools/harness_buddy.py check")
    else:
        lines.append("다음 행동: 필요하면 check 모드로 다시 검증")
    return lines


def build_state_snapshot(harness_path: Path, state_path: Path) -> dict[str, object]:
    values = load_harness_values(harness_path)
    last_check: dict[str, str] = {
        "status": "unknown",
        "checked_at": "unknown",
        "freshness": "알 수 없음",
    }
    buddy_state = "waiting"
    buddy_message = "검증 기록이 없습니다."

    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        stored_last_check = state.get("last_check", {})
        freshness = get_freshness_label(stored_last_check.get("checked_at"))
        last_check = {
            "status": stored_last_check.get("status", "unknown"),
            "checked_at": stored_last_check.get("checked_at", "unknown"),
            "freshness": freshness,
        }
        if stored_last_check.get("status") == "failed":
            buddy_state = "needs_review"
            buddy_message = "검증 실패를 점검해야 합니다."
        elif freshness == "오래됨":
            buddy_state = "stale"
            buddy_message = "검증 기록이 오래되었습니다."
        elif stored_last_check.get("status") == "passed":
            buddy_state = "ready"
            buddy_message = "검증이 최신입니다."

    return {
        "project": values["project_name"],
        "stage": values["current_stage"],
        "last_check": last_check,
        "buddy": {
            "state": buddy_state,
            "message": buddy_message,
        },
    }


def find_missing_fields(harness_text: str) -> list[str]:
    missing = []
    for label, heading in REQUIRED_FIELDS:
        if not read_code_block_after_heading(harness_text, heading):
            missing.append(label)
    return missing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Codex Harness Buddy CLI")
    parser.add_argument(
        "command",
        nargs="?",
        help="Buddy 출력 모드 또는 prompt",
    )
    parser.add_argument(
        "prompt_mode",
        nargs="?",
        help="prompt 명령에 사용할 Buddy 모드 또는 nudge 입력",
    )
    parser.add_argument(
        "--harness-path",
        default=str(HARNESS_PATH),
        help="읽을 HARNESS.md 경로",
    )
    parser.add_argument(
        "--state-path",
        default=str(STATE_PATH),
        help="읽고 쓸 buddy_state.json 경로",
    )
    parser.add_argument(
        "--character-only",
        action="store_true",
        help="character 명령에서 개발자 패널을 숨긴 캐릭터 중심 모드로 시작",
    )
    args = parser.parse_args()

    if args.command == "prompt":
        if args.prompt_mode not in MODES:
            parser.error("prompt 명령에는 fast, careful, review 중 하나가 필요합니다.")
    elif args.command == "nudge":
        if not args.prompt_mode:
            parser.error("nudge 명령에는 자연어 입력이 필요합니다.")
    elif args.command and args.command not in COMMANDS:
        parser.error("명령은 fast, careful, review, prompt, check, status, nudge, evaluate-nudge, state-json, manual-check, character, help 중 하나여야 합니다.")
    elif args.command == "character":
        if args.prompt_mode:
            parser.error("character 명령에는 두 번째 위치 인자를 사용할 수 없습니다.")
    elif args.prompt_mode:
        parser.error("두 번째 위치 인자는 prompt 명령에서만 사용할 수 있습니다.")
    elif args.character_only:
        parser.error("--character-only 옵션은 character 명령에서만 사용할 수 있습니다.")

    return args


def main() -> int:
    args = parse_args()
    harness_path = Path(args.harness_path)
    state_path = Path(args.state_path)

    if args.command == "help":
        print("\n".join(load_help_summary()))
        return 0

    if args.command == "manual-check":
        print("\n".join(load_manual_check_summary()))
        return 0

    if args.command == "character":
        return run_character_ui(args.character_only)

    if not harness_path.exists():
        print("HARNESS.md를 찾지 못했습니다.")
        print("현재 프로젝트의 HARNESS.md 경로를 확인하거나 --harness-path로 지정해주세요.")
        return 1

    harness_text = harness_path.read_text(encoding="utf-8")
    missing_fields = find_missing_fields(harness_text)
    if missing_fields:
        print("HARNESS.md에서 필수 항목을 읽지 못했습니다.")
        print("누락 항목: " + ", ".join(missing_fields))
        return 1

    if args.command == "check":
        return run_project_check(state_path)

    if args.command == "evaluate-nudge":
        return run_nudge_evaluation()

    if args.command == "status":
        print("\n".join(load_status_summary(harness_path, state_path)))
        return 0

    if args.command == "state-json":
        print(json.dumps(build_state_snapshot(harness_path, state_path), ensure_ascii=False, indent=2))
        return 0

    if args.command == "prompt":
        values = load_harness_values(harness_path)
        print("\n".join(load_prompt(args.prompt_mode, values["smoke_command"])))
    elif args.command == "nudge":
        print("\n".join(load_nudge_summary(args.prompt_mode, state_path)))
    elif args.command:
        print("\n".join(load_mode_summary(harness_path, args.command, state_path)))
    else:
        print("\n".join(load_summary(harness_path)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
