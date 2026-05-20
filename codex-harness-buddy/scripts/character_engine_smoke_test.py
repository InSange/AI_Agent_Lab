import importlib.util
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = PROJECT_ROOT / "tools" / "buddy_character_engine.py"


def load_engine_module():
    spec = importlib.util.spec_from_file_location("buddy_character_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("buddy_character_engine.py를 import할 수 없습니다.")

    module = importlib.util.module_from_spec(spec)
    # 파일 경로로 직접 불러온 모듈도 일반 import처럼 같은 모듈 캐시에 등록한다.
    sys.modules["buddy_character_engine"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if not ENGINE_PATH.exists():
        print("character engine smoke test 실패: tools/buddy_character_engine.py가 없습니다.")
        return 1

    module = load_engine_module()

    if module.character_face("ready") != "(^_^)":
        print("character engine smoke test 실패: ready 얼굴 매핑이 예상과 다릅니다.")
        return 1

    if module.character_label("needs_review") != "점검 필요":
        print("character engine smoke test 실패: needs_review 라벨 매핑이 예상과 다릅니다.")
        return 1

    if module.character_reaction("stale") != "검증이 조금 오래됐어요. 한 번 확인해볼까요?":
        print("character engine smoke test 실패: stale 반응 문구가 예상과 다릅니다.")
        return 1

    if module.character_mood("ready") != "calm":
        print("character engine smoke test 실패: ready mood 매핑이 예상과 다릅니다.")
        return 1

    if module.character_frame("calm", tick=0) != "(^_^)":
        print("character engine smoke test 실패: calm 첫 프레임이 예상과 다릅니다.")
        return 1

    if module.character_frame("calm", tick=1) != "(^.^)":
        print("character engine smoke test 실패: calm 두 번째 프레임이 예상과 다릅니다.")
        return 1

    if module.character_frame("energetic", tick=3) != "(^o^)":
        print("character engine smoke test 실패: energetic 프레임 순환이 예상과 다릅니다.")
        return 1

    if module.character_frame("unknown", tick=0) != "(?)":
        print("character engine smoke test 실패: 알 수 없는 mood 프레임이 예상과 다릅니다.")
        return 1

    sample_state = {
        "buddy": {
            "state": "ready",
            "message": "검증이 최신입니다.",
        }
    }
    view_model = module.build_character_view_model(sample_state)
    if view_model["face"] != "(^_^)" or view_model["message"] != "검증이 최신입니다." or view_model["mood"] != "calm":
        print("character engine smoke test 실패: 상태 스냅샷 표시 모델이 예상과 다릅니다.")
        return 1

    preview_model = module.build_preview_view_model("needs_review")
    if preview_model["label"] != "점검 필요" or preview_model["mood"] != "stressed" or "Refresh" not in preview_model["message"]:
        print("character engine smoke test 실패: Preview 표시 모델이 예상과 다릅니다.")
        return 1

    check_model = module.build_check_running_view_model()
    if check_model["label"] != "검증 중" or check_model["reaction"] != "검증을 돌리고 있어요." or check_model["mood"] != "working":
        print("character engine smoke test 실패: Check 실행 중 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_fast_model = module.build_nudge_reaction_view_model("빨리 해줘")
    if nudge_fast_model["label"] != "빠르게" or nudge_fast_model["face"] != "(^.^)" or nudge_fast_model["mood"] != "energetic":
        print("character engine smoke test 실패: 빠른 Nudge 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_careful_model = module.build_nudge_reaction_view_model("조심해서 해줘")
    if nudge_careful_model["label"] != "신중하게" or nudge_careful_model["reaction"] != "조심해서 살펴볼게요.":
        print("character engine smoke test 실패: 신중 Nudge 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_check_model = module.build_nudge_reaction_view_model("검증해줘")
    if nudge_check_model["label"] != "검증 준비" or nudge_check_model["reaction"] != "검증 쪽으로 확인해볼게요.":
        print("character engine smoke test 실패: 검증 Nudge 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_status_model = module.build_nudge_reaction_view_model("상태 어때")
    if nudge_status_model["label"] != "상태 확인" or nudge_status_model["reaction"] != "현재 상태를 확인해볼게요.":
        print("character engine smoke test 실패: 상태 Nudge 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_review_model = module.build_nudge_reaction_view_model("마무리해도 돼?")
    if nudge_review_model["label"] != "점검 준비" or nudge_review_model["reaction"] != "마무리 상태를 점검해볼게요.":
        print("character engine smoke test 실패: review Nudge 표시 모델이 예상과 다릅니다.")
        return 1

    nudge_default_model = module.build_nudge_reaction_view_model("뭐 하지")
    if nudge_default_model["label"] != "해석 중" or nudge_default_model["mood"] != "curious":
        print("character engine smoke test 실패: 기본 Nudge 표시 모델이 예상과 다릅니다.")
        return 1

    if module.remaining_display_ms(started_at_ms=1000, now_ms=1500) != 300:
        print("character engine smoke test 실패: 반응 최소 표시 시간 계산이 예상과 다릅니다.")
        return 1

    print("character engine smoke test 성공")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
