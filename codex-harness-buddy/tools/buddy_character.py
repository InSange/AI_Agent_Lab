from pathlib import Path
from datetime import datetime
import json
import os
import subprocess
import sys
import threading
import time
import tkinter as tk


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PROJECT_ROOT / "tools" / "harness_buddy.py"
WINDOW_TITLE = "Codex Harness Buddy Character"
WINDOW_GEOMETRY = "430x455"
RESULT_WRAP_LENGTH = 380
RESULT_LABEL_HEIGHT = 3
REFRESH_BUTTON_LABEL = "Refresh"
CHECK_BUTTON_LABEL = "Check"
NUDGE_BUTTON_LABEL = "Nudge"
NUDGE_EXAMPLE_LABEL = "예시 입력"
CHECK_GROUP_LABEL = "검증"
COMMAND_GROUP_LABEL = "명령"
NUDGE_GROUP_LABEL = "Nudge"
PREVIEW_GROUP_LABEL = "Preview 확인"
PREVIEW_HELP_LABEL = "표시만 바뀜 · Refresh로 복귀"
ALWAYS_ON_TOP_LABEL = "항상 위"
CHECK_RUNNING_MESSAGE = "검증 실행 중..."
CHECK_SUCCESS_MESSAGE = "검증 성공. 상태를 갱신했습니다."
CHECK_FAILURE_MESSAGE = "검증 실행에 실패했습니다."
CHECK_RUNNING_FACE = "(o_o)"
CHECK_RUNNING_LABEL = "검증 중"
CHECK_RUNNING_REACTION = "검증을 돌리고 있어요."
CHECK_RUNNING_STATUS_MESSAGE = "잠시만 기다려 주세요."
REACTION_MIN_DISPLAY_MS = 800

ACTION_BUTTON_COMMANDS = {
    "Status": ["status"],
    "Review": ["review"],
    "Fast": ["prompt", "fast"],
    "Careful": ["prompt", "careful"],
}

NUDGE_EXAMPLES = {
    "검증해줘": "검증해줘",
    "빨리": "빨리 해줘",
    "조심": "조심해서 해줘",
    "상태확인": "상태 어때",
}

NUDGE_REACTION_RULES = (
    (("빨리", "대충"), "(^.^)", "빠르게", "빠른 흐름으로 맞춰볼게요."),
    (("조심", "불안"), "(-.-)", "신중하게", "조심해서 살펴볼게요."),
    (("검증", "테스트", "되는지"), "(o_o)", "검증 준비", "검증 쪽으로 확인해볼게요."),
)
NUDGE_DEFAULT_REACTION = ("(._.)", "해석 중", "무슨 뜻인지 살펴보고 있어요.")
NUDGE_REACTION_MESSAGE = "Nudge 반응입니다. 결과가 오면 요약을 보여줍니다."

PREVIEW_STATES = {
    "Ready": "ready",
    "Stale": "stale",
    "Waiting": "waiting",
    "Needs Review": "needs_review",
}

SUMMARY_PREFIXES = (
    "추천 명령:",
    "다음 명령:",
    "운영 모드:",
    "마지막 검증:",
    "다음 행동:",
    "이 세션에서는",
)

ACTION_SUMMARY_PREFIXES = {
    "Status": (
        "마지막 검증:",
        "검증 상태:",
        "다음 행동:",
    ),
    "Review": (
        "다음 행동:",
        "마지막 검증:",
        "검증 상태:",
        "운영 모드:",
    ),
    "Fast": (
        "이 세션에서는",
        "짧게 판단",
        "검증 명령은",
    ),
    "Careful": (
        "이 세션에서는",
        "승인 규칙과 검증을",
        "검증 명령은",
    ),
    "Nudge": (
        "다음 명령:",
        "추천 명령:",
        "감지된 의도:",
    ),
}

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


def build_state_command() -> list[str]:
    return [sys.executable, "harness_buddy.py", "state-json"]


def build_check_command() -> list[str]:
    return [sys.executable, "harness_buddy.py", "check"]


def build_cli_command(args: list[str]) -> list[str]:
    return [sys.executable, "harness_buddy.py", *args]


def running_action_message(label: str) -> str:
    return f"{label} 실행 중..."


def completed_action_message(label: str, returncode: int) -> str:
    if returncode == 0:
        return f"{label} 완료"
    return f"{label} 실패"


def character_face(state: str) -> str:
    return CHARACTER_FACES.get(state, "(?)")


def character_label(state: str) -> str:
    return CHARACTER_LABELS.get(state, "알 수 없음")


def character_reaction(state: str) -> str:
    return CHARACTER_REACTIONS.get(state, "상태를 읽는 중이에요.")


def current_refresh_time() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")


def current_millis() -> int:
    return int(time.monotonic() * 1000)


def remaining_display_ms(started_at_ms: int, now_ms: int) -> int:
    elapsed_ms = max(0, now_ms - started_at_ms)
    return max(0, REACTION_MIN_DISPLAY_MS - elapsed_ms)


def refresh_time_label(refresh_time: str) -> str:
    return f"마지막 갱신: {refresh_time}"


def load_state_snapshot() -> dict[str, object]:
    result = subprocess.run(
        build_state_command(),
        cwd=CLI_PATH.parent,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    if result.returncode != 0:
        return {
            "buddy": {
                "state": "needs_review",
                "message": "상태를 읽지 못했습니다.",
            }
        }
    return json.loads(result.stdout)


def run_buddy_check() -> int:
    result = subprocess.run(
        build_check_command(),
        cwd=CLI_PATH.parent,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    return result.returncode


def run_buddy_command(args: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        build_cli_command(args),
        cwd=CLI_PATH.parent,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    output = result.stdout.strip()
    if result.stderr.strip():
        output = f"{output}\n{result.stderr.strip()}".strip()
    return result.returncode, output


def summarize_output(output: str, prefixes: tuple[str, ...] = SUMMARY_PREFIXES) -> str:
    return "\n".join(summarize_output_lines(output, prefixes, limit=1))


def summarize_output_lines(output: str, prefixes: tuple[str, ...] = SUMMARY_PREFIXES, limit: int = 2) -> list[str]:
    lines = [line.strip() for line in output.strip().splitlines() if line.strip()]
    summaries: list[str] = []
    for prefix in prefixes:
        summary = next((line for line in lines if line.startswith(prefix) and line not in summaries), "")
        if summary:
            summaries.append(summary)
        if len(summaries) >= limit:
            break
    if not summaries and lines:
        summaries.append(lines[0])
    return [truncate_summary_line(summary) for summary in summaries]


def truncate_summary_line(summary: str) -> str:
    if len(summary) > 80:
        return summary[:77] + "..."
    return summary


def summarize_action_output(label: str, output: str) -> str:
    return "\n".join(summarize_output_lines(output, ACTION_SUMMARY_PREFIXES.get(label, SUMMARY_PREFIXES), limit=2))


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
    }


def build_preview_view_model(state: str) -> dict[str, str]:
    return {
        "face": character_face(state),
        "label": character_label(state),
        "reaction": character_reaction(state),
        "message": "프리뷰 상태입니다. Refresh를 누르면 실제 상태로 돌아갑니다.",
    }


def build_check_running_view_model() -> dict[str, str]:
    return {
        "face": CHECK_RUNNING_FACE,
        "label": CHECK_RUNNING_LABEL,
        "reaction": CHECK_RUNNING_REACTION,
        "message": CHECK_RUNNING_STATUS_MESSAGE,
    }


def build_nudge_reaction_view_model(user_input: str) -> dict[str, str]:
    for keywords, face, label, reaction in NUDGE_REACTION_RULES:
        if any(keyword in user_input for keyword in keywords):
            return {
                "face": face,
                "label": label,
                "reaction": reaction,
                "message": NUDGE_REACTION_MESSAGE,
            }
    face, label, reaction = NUDGE_DEFAULT_REACTION
    return {
        "face": face,
        "label": label,
        "reaction": reaction,
        "message": NUDGE_REACTION_MESSAGE,
    }


class CharacterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(390, 360)

        self.face_var = tk.StringVar()
        self.label_var = tk.StringVar()
        self.reaction_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.refresh_time_var = tk.StringVar()
        self.always_on_top_var = tk.BooleanVar(value=False)
        self.action_buttons: list[tk.Button] = []
        self.nudge_reaction_started_at_ms = 0
        self.check_reaction_started_at_ms = 0

        option_frame = tk.Frame(root)
        option_frame.pack(fill="x", padx=10, pady=(8, 0))
        tk.Checkbutton(
            option_frame,
            text=ALWAYS_ON_TOP_LABEL,
            variable=self.always_on_top_var,
            command=self.toggle_always_on_top,
        ).pack(side="right")

        tk.Label(root, textvariable=self.face_var, font=("Consolas", 28)).pack(pady=(6, 4))
        tk.Label(root, textvariable=self.label_var, font=("Segoe UI", 12, "bold")).pack()
        tk.Label(root, textvariable=self.reaction_var, font=("Segoe UI", 9), wraplength=360).pack(pady=(4, 0))
        tk.Label(root, textvariable=self.message_var, wraplength=320).pack(pady=(4, 4))
        tk.Label(
            root,
            textvariable=self.result_var,
            font=("Segoe UI", 9),
            wraplength=RESULT_WRAP_LENGTH,
            height=RESULT_LABEL_HEIGHT,
        ).pack(fill="x", padx=10, pady=(0, 4))
        tk.Label(root, textvariable=self.refresh_time_var, font=("Segoe UI", 8)).pack(pady=(0, 8))

        button_frame = tk.Frame(root)
        button_frame.pack(pady=(0, 4))
        tk.Label(button_frame, text=CHECK_GROUP_LABEL, width=8, anchor="w", font=("Segoe UI", 8)).pack(side="left")
        self.check_button = tk.Button(button_frame, text=CHECK_BUTTON_LABEL, command=self.start_check)
        self.check_button.pack(side="left", padx=4)
        self.refresh_button = tk.Button(button_frame, text=REFRESH_BUTTON_LABEL, command=self.refresh_state)
        self.refresh_button.pack(side="left", padx=4)

        action_frame = tk.Frame(root)
        action_frame.pack(pady=(0, 4))
        tk.Label(action_frame, text=COMMAND_GROUP_LABEL, width=8, anchor="w", font=("Segoe UI", 8)).pack(side="left")
        for label, args in ACTION_BUTTON_COMMANDS.items():
            button = tk.Button(
                action_frame,
                text=label,
                command=lambda action_label=label, command_args=args: self.run_action(action_label, command_args),
            )
            button.pack(side="left", padx=3)
            self.action_buttons.append(button)

        nudge_frame = tk.Frame(root)
        nudge_frame.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(nudge_frame, text=NUDGE_GROUP_LABEL, width=8, anchor="w", font=("Segoe UI", 8)).pack(side="left")
        self.nudge_entry = tk.Entry(nudge_frame)
        self.nudge_entry.pack(side="left", fill="x", expand=True)
        self.nudge_button = tk.Button(nudge_frame, text=NUDGE_BUTTON_LABEL, command=self.run_nudge)
        self.nudge_button.pack(side="left", padx=(6, 0))
        self.action_buttons.append(self.nudge_button)

        example_frame = tk.Frame(root)
        example_frame.pack(pady=(0, 10))
        tk.Label(example_frame, text=NUDGE_EXAMPLE_LABEL, font=("Segoe UI", 8)).pack(side="left", padx=(0, 4))
        for label, text in NUDGE_EXAMPLES.items():
            tk.Button(
                example_frame,
                text=label,
                command=lambda example_text=text: self.fill_nudge_example(example_text),
            ).pack(side="left", padx=3)

        preview_frame = tk.Frame(root)
        preview_frame.pack(pady=(0, 8))
        tk.Label(preview_frame, text=PREVIEW_GROUP_LABEL, font=("Segoe UI", 8)).pack(side="left", padx=(0, 4))
        tk.Label(preview_frame, text=PREVIEW_HELP_LABEL, font=("Segoe UI", 8)).pack(side="left", padx=(0, 6))
        for label, state in PREVIEW_STATES.items():
            tk.Button(
                preview_frame,
                text=label,
                command=lambda preview_state=state: self.preview_state(preview_state),
            ).pack(side="left", padx=3)

        self.refresh_state()
        self.apply_always_on_top(False)

    def apply_view_model(self, view_model: dict[str, str]) -> None:
        self.face_var.set(view_model["face"])
        self.label_var.set(view_model["label"])
        self.reaction_var.set(view_model["reaction"])
        self.message_var.set(view_model["message"])

    def refresh_state(self) -> None:
        self.apply_view_model(build_character_view_model(load_state_snapshot()))
        self.refresh_time_var.set(refresh_time_label(current_refresh_time()))

    def set_check_enabled(self, enabled: bool) -> None:
        self.check_button.configure(state="normal" if enabled else "disabled")

    def set_refresh_enabled(self, enabled: bool) -> None:
        self.refresh_button.configure(state="normal" if enabled else "disabled")

    def set_action_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for button in self.action_buttons:
            button.configure(state=state)

    def set_result_message(self, message: str) -> None:
        self.result_var.set(message)

    def apply_always_on_top(self, enabled: bool) -> None:
        self.root.attributes("-topmost", bool(enabled))

    def toggle_always_on_top(self) -> None:
        self.apply_always_on_top(self.always_on_top_var.get())

    def start_worker(self, label: str, args: list[str]) -> None:
        self.set_check_enabled(False)
        self.set_refresh_enabled(False)
        self.set_action_enabled(False)
        self.set_result_message(running_action_message(label))
        worker = threading.Thread(target=lambda: self.run_action_worker(label, args), daemon=True)
        worker.start()

    def run_action(self, label: str, args: list[str]) -> None:
        self.start_worker(label, args)

    def run_nudge(self) -> None:
        user_input = self.nudge_entry.get().strip()
        if not user_input:
            self.set_result_message("Nudge 입력이 비어 있습니다.")
            return
        self.nudge_reaction_started_at_ms = current_millis()
        self.apply_view_model(build_nudge_reaction_view_model(user_input))
        self.refresh_time_var.set(refresh_time_label(current_refresh_time()))
        self.start_worker(NUDGE_BUTTON_LABEL, ["nudge", user_input])

    def fill_nudge_example(self, text: str) -> None:
        self.nudge_entry.delete(0, tk.END)
        self.nudge_entry.insert(0, text)
        self.set_result_message(f"Nudge 입력 준비: {text}")

    def preview_state(self, state: str) -> None:
        self.apply_view_model(build_preview_view_model(state))
        self.set_result_message("상태 프리뷰입니다. 실제 상태 파일은 바꾸지 않았습니다.")
        self.refresh_time_var.set(refresh_time_label(current_refresh_time()))

    def run_action_worker(self, label: str, args: list[str]) -> None:
        returncode, output = run_buddy_command(args)
        delay_ms = 0
        if label == NUDGE_BUTTON_LABEL:
            delay_ms = remaining_display_ms(self.nudge_reaction_started_at_ms, current_millis())
        self.root.after(delay_ms, lambda: self.finish_action(label, returncode, output))

    def finish_action(self, label: str, returncode: int, output: str) -> None:
        summary = summarize_action_output(label, output)
        message = completed_action_message(label, returncode)
        if summary:
            message = f"{message}: {summary}"
        self.set_result_message(message)
        self.refresh_time_var.set(refresh_time_label(current_refresh_time()))
        if label in {"Status", "Review"}:
            self.refresh_state()
            self.set_result_message(message)
        self.set_check_enabled(True)
        self.set_refresh_enabled(True)
        self.set_action_enabled(True)

    def start_check(self) -> None:
        self.set_check_enabled(False)
        self.set_refresh_enabled(False)
        self.set_action_enabled(False)
        self.check_reaction_started_at_ms = current_millis()
        self.apply_view_model(build_check_running_view_model())
        self.refresh_time_var.set(refresh_time_label(current_refresh_time()))
        self.set_result_message(CHECK_RUNNING_MESSAGE)
        worker = threading.Thread(target=self.run_check_worker, daemon=True)
        worker.start()

    def run_check(self) -> None:
        self.start_check()

    def run_check_worker(self) -> None:
        returncode = run_buddy_check()
        delay_ms = remaining_display_ms(self.check_reaction_started_at_ms, current_millis())
        self.root.after(delay_ms, lambda: self.finish_check(returncode))

    def finish_check(self, returncode: int) -> None:
        if returncode != 0:
            self.set_result_message(CHECK_FAILURE_MESSAGE)
            self.refresh_time_var.set(refresh_time_label(current_refresh_time()))
            self.set_check_enabled(True)
            self.set_refresh_enabled(True)
            self.set_action_enabled(True)
            return
        self.refresh_state()
        self.set_result_message(CHECK_SUCCESS_MESSAGE)
        self.set_check_enabled(True)
        self.set_refresh_enabled(True)
        self.set_action_enabled(True)


def main() -> int:
    root = tk.Tk()
    CharacterApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
