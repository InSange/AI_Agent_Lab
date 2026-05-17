CHARACTER_STATE_LABELS = {
    "ready": "준비됨",
    "stale": "검증 오래됨",
    "waiting": "대기 중",
    "needs_review": "점검 필요",
}


def character_state_label(state: str) -> str:
    return CHARACTER_STATE_LABELS.get(state, "알 수 없음")


def main() -> int:
    print("캐릭터 상태 매핑 테스트")

    for state, expected_label in CHARACTER_STATE_LABELS.items():
        actual_label = character_state_label(state)
        if actual_label != expected_label:
            print(f"[FAIL] {state} -> {actual_label} (기대: {expected_label})")
            return 1
        print(f"[OK] {state} -> {actual_label}")

    print("캐릭터 상태 매핑 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
