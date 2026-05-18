CHARACTER_FACES = {
    "ready": "(^_^)",
    "stale": "(-_-)",
    "waiting": "(._.)",
    "needs_review": "(>_<)",
}

CHARACTER_LABELS = {
    "ready": "준비됨",
    "stale": "검증 오래됨",
    "waiting": "대기 중",
    "needs_review": "점검 필요",
}

CHARACTER_REACTIONS = {
    "ready": "좋아요. 검증은 최신이에요.",
    "stale": "검증이 조금 오래됐어요. 한 번 확인해볼까요?",
    "waiting": "아직 검증 기록을 기다리는 중이에요.",
    "needs_review": "점검이 필요해요. 실패 로그부터 볼게요.",
}

CHARACTER_MOODS = {
    "ready": "calm",
    "stale": "sleepy",
    "waiting": "idle",
    "needs_review": "stressed",
}

CHECK_RUNNING_FACE = "(o_o)"
CHECK_RUNNING_LABEL = "검증 중"
CHECK_RUNNING_REACTION = "검증을 돌리고 있어요."
CHECK_RUNNING_STATUS_MESSAGE = "잠시만 기다려 주세요."
CHECK_RUNNING_MOOD = "working"
REACTION_MIN_DISPLAY_MS = 800

NUDGE_REACTION_RULES = (
    (("빨리", "대충"), "(^.^)", "빠르게", "빠른 흐름으로 맞춰볼게요.", "energetic"),
    (("조심", "불안"), "(-.-)", "신중하게", "조심해서 살펴볼게요.", "focused"),
    (("검증", "테스트", "되는지"), "(o_o)", "검증 준비", "검증 쪽으로 확인해볼게요.", "working"),
)
NUDGE_DEFAULT_REACTION = ("(._.)", "해석 중", "무슨 뜻인지 살펴보고 있어요.", "curious")
NUDGE_REACTION_MESSAGE = "Nudge 반응입니다. 결과가 오면 요약을 보여줍니다."


def character_face(state: str) -> str:
    return CHARACTER_FACES.get(state, "(?)")


def character_label(state: str) -> str:
    return CHARACTER_LABELS.get(state, "알 수 없음")


def character_reaction(state: str) -> str:
    return CHARACTER_REACTIONS.get(state, "상태를 읽는 중이에요.")


def character_mood(state: str) -> str:
    return CHARACTER_MOODS.get(state, "unknown")


def remaining_display_ms(started_at_ms: int, now_ms: int) -> int:
    elapsed_ms = max(0, now_ms - started_at_ms)
    return max(0, REACTION_MIN_DISPLAY_MS - elapsed_ms)


def build_character_view_model(snapshot: dict[str, object]) -> dict[str, str]:
    buddy = snapshot.get("buddy", {})
    if not isinstance(buddy, dict):
        buddy = {}
    state = str(buddy.get("state", "waiting"))
    message = str(buddy.get("message", "상태를 기다리는 중입니다."))
    return {
        "face": character_face(state),
        "label": character_label(state),
        "reaction": character_reaction(state),
        "message": message,
        "mood": character_mood(state),
    }


def build_preview_view_model(state: str) -> dict[str, str]:
    return {
        "face": character_face(state),
        "label": character_label(state),
        "reaction": character_reaction(state),
        "message": "프리뷰 상태입니다. Refresh를 누르면 실제 상태로 돌아갑니다.",
        "mood": character_mood(state),
    }


def build_check_running_view_model() -> dict[str, str]:
    return {
        "face": CHECK_RUNNING_FACE,
        "label": CHECK_RUNNING_LABEL,
        "reaction": CHECK_RUNNING_REACTION,
        "message": CHECK_RUNNING_STATUS_MESSAGE,
        "mood": CHECK_RUNNING_MOOD,
    }


def build_nudge_reaction_view_model(user_input: str) -> dict[str, str]:
    for keywords, face, label, reaction, mood in NUDGE_REACTION_RULES:
        if any(keyword in user_input for keyword in keywords):
            return {
                "face": face,
                "label": label,
                "reaction": reaction,
                "message": NUDGE_REACTION_MESSAGE,
                "mood": mood,
            }
    face, label, reaction, mood = NUDGE_DEFAULT_REACTION
    return {
        "face": face,
        "label": label,
        "reaction": reaction,
        "message": NUDGE_REACTION_MESSAGE,
        "mood": mood,
    }
