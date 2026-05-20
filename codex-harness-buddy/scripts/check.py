from pathlib import Path
import os
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    ("CLI 실행", [sys.executable, str(PROJECT_ROOT / "tools" / "harness_buddy.py")]),
    ("smoke test", [sys.executable, str(PROJECT_ROOT / "scripts" / "smoke_test.py")]),
    ("UI smoke test", [sys.executable, str(PROJECT_ROOT / "scripts" / "ui_smoke_test.py")]),
    ("model adapter smoke test", [sys.executable, str(PROJECT_ROOT / "scripts" / "model_adapter_smoke_test.py")]),
    ("character engine smoke test", [sys.executable, str(PROJECT_ROOT / "scripts" / "character_engine_smoke_test.py")]),
    ("character UI smoke test", [sys.executable, str(PROJECT_ROOT / "scripts" / "character_ui_smoke_test.py")]),
]

CHECK_SUMMARY = [
    "- CLI: 기본 실행과 HARNESS 읽기 확인",
    "- smoke test: 모드, 상태 파일, nudge 규칙 확인",
    "- UI smoke test: 버튼 계약과 UI 헬퍼 확인",
    "- model adapter smoke test: 모델 연결 준비용 의도 분류 어댑터 확인",
    "- character engine smoke test: 캐릭터 상태/반응 표시 모델 확인",
    "- character UI smoke test: 캐릭터 창 상태 표시와 조작 버튼 계약 확인",
    "- nudge 평가: 별도 실행 대상",
]

PROJECT_OPTIONAL_CHECKS = [
    "- nudge 평가: python tools/harness_buddy.py evaluate-nudge",
    "- 캐릭터 UI 수동 확인: python tools/harness_buddy.py character --character-only",
    "- UI 수동 확인: python tools/buddy_ui.py",
]

ROOT_OPTIONAL_CHECKS = [
    "- nudge 평가: python codex-harness-buddy\\tools\\harness_buddy.py evaluate-nudge",
    "- 캐릭터 UI 수동 확인: python codex-harness-buddy\\tools\\harness_buddy.py character --character-only",
    "- UI 수동 확인: python codex-harness-buddy\\tools\\buddy_ui.py",
]

MANUAL_CHECK_GROUPS = [
    (
        "[레이아웃]",
        [
            "- 캐릭터 UI: Review 후 Nudge 입력창이 보이는지",
            "- 캐릭터 UI: 예시 입력 버튼이 의미 있게 보이는지",
            "- 캐릭터 UI: 개발자 패널 체크 해제 시 버튼/입력/Preview가 숨겨지는지",
            "- 캐릭터 UI: --character-only 실행 시 개발자 패널이 숨겨진 상태로 시작하는지",
        ],
    ),
    (
        "[상호작용]",
        [
            "- 캐릭터 UI: Check 실행 중 얼굴과 라벨이 검증 중으로 바뀌는지",
            "- 캐릭터 UI: 예시 입력 후 Nudge 실행 결과가 표시되는지",
            "- 캐릭터 UI: Nudge 입력에 따라 빠르게/신중하게/검증 준비/상태 확인/점검 준비 라벨이 바뀌는지",
            "- 캐릭터 UI: mood에 따라 ASCII 얼굴이 살짝 바뀌는지",
            "- 캐릭터 UI: Nudge/Check 반응 라벨이 너무 빨리 사라지지 않는지",
            "- 캐릭터 UI: 항상 위 체크/해제 시 창 z축 동작이 바뀌는지",
        ],
    ),
    (
        "[Preview]",
        [
            "- 캐릭터 UI: Waiting/Needs Review 프리뷰에서 얼굴, 라벨, 반응 문구가 바뀌는지",
            "- 캐릭터 UI: Preview 확인 후 Refresh로 실제 상태에 돌아오는지",
            "- 캐릭터 UI: Preview 안내 문구가 표시 변경과 Refresh 복귀를 이해시키는지",
        ],
    ),
]


def print_success_summary() -> None:
    print("검증 요약")
    for line in CHECK_SUMMARY:
        print(line)
    print("선택 검증")
    print("프로젝트 폴더:")
    for line in PROJECT_OPTIONAL_CHECKS:
        print(line)
    print("루트 폴더:")
    for line in ROOT_OPTIONAL_CHECKS:
        print(line)
    print("다음 확인: 캐릭터 창은 필요 시 직접 실행해 버튼과 상태 표시를 확인")
    print("수동 확인:")
    for group_label, checks in MANUAL_CHECK_GROUPS:
        print(group_label)
        for line in checks:
            print(line)


def run_check(name: str, command: list[str]) -> bool:
    print(f"[RUN] {name}")
    result = subprocess.run(
        command,
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

    if result.returncode != 0:
        print(f"[FAIL] {name}")
        return False

    print(f"[OK] {name}")
    return True


def main() -> int:
    print("Codex Harness Buddy 검증 파이프라인")

    if os.environ.get("HARNESS_BUDDY_FORCE_CHECK_FAILURE") == "1":
        print("강제 실패: smoke test 실패 예시")
        print("전체 검증 실패")
        return 1

    for name, command in CHECKS:
        if not run_check(name, command):
            print(f"검증 요약: {name} 단계에서 실패")
            print("전체 검증 실패")
            return 1

    print_success_summary()
    print("전체 검증 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
