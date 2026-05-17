from pathlib import Path
from dataclasses import dataclass
import os
import subprocess
import sys
import tkinter as tk
from tkinter import scrolledtext


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PROJECT_ROOT / "tools" / "harness_buddy.py"
WINDOW_TITLE = "Codex Harness Buddy"
COPY_BUTTON_LABEL = "Copy Output"
COPY_PROMPT_BUTTON_LABEL = "Copy Prompt"

BUTTON_COMMANDS = {
    "Check": ["check"],
    "Status": ["status"],
    "Review Status": ["review"],
    "Fast": ["prompt", "fast"],
    "Careful": ["prompt", "careful"],
    "Review Prompt": ["prompt", "review"],
}

BUTTON_GROUPS = [
    ("상태", ["Check", "Status", "Review Status"]),
    ("프롬프트", ["Fast", "Careful", "Review Prompt"]),
]


@dataclass
class CommandResult:
    output: str
    returncode: int


def build_cli_command(args: list[str]) -> list[str]:
    return [sys.executable, "harness_buddy.py", *args]


def command_label(args: list[str]) -> str:
    return " ".join(args)


def running_status(args: list[str]) -> str:
    return f"실행 중: {command_label(args)}"


def completed_status(args: list[str], returncode: int) -> str:
    if returncode == 0:
        return f"완료: {command_label(args)}"
    return f"실패: {command_label(args)}"


def copy_status() -> str:
    return "완료: 출력 복사"


def copy_prompt_status() -> str:
    return "완료: 프롬프트 복사"


def missing_prompt_status() -> str:
    return "복사할 프롬프트가 없습니다"


def missing_prompt_should_clear_clipboard() -> bool:
    return True


def cleared_clipboard_text() -> str:
    return ""


def clipboard_text(text: str) -> str:
    return text.strip()


def is_prompt_command(args: list[str]) -> bool:
    return len(args) == 2 and args[0] == "prompt"


def should_keep_prompt(args: list[str], returncode: int) -> bool:
    return returncode == 0 and is_prompt_command(args)


def should_clear_prompt(args: list[str], returncode: int) -> bool:
    return not should_keep_prompt(args, returncode)


def buddy_state_after(source_label: str, returncode: int) -> str:
    if returncode != 0:
        return "점검 필요"

    states = {
        "Check": "준비됨",
        "Status": "상태 확인됨",
        "Review Status": "검토 중",
        "Fast": "빠른 지시문 준비",
        "Careful": "신중 지시문 준비",
        "Review Prompt": "리뷰 지시문 준비",
        "Nudge": "입력 해석됨",
    }
    return states.get(source_label, "대기 중")


def buddy_state_label(state: str) -> str:
    return f"Buddy 상태: {state}"


def output_header(source_label: str, args: list[str], buddy_state: str | None = None) -> str:
    lines = [f"[{source_label} 실행]", f"명령: {command_label(args)}"]
    if buddy_state:
        lines.append(buddy_state_label(buddy_state))
    return "\n".join(lines) + "\n"


def nudge_header(user_input: str, buddy_state: str | None = None) -> str:
    lines = ["[Nudge 해석]", f"입력: {user_input}", "명령: nudge"]
    if buddy_state:
        lines.append(buddy_state_label(buddy_state))
    return "\n".join(lines) + "\n"


def run_buddy_command(args: list[str]) -> CommandResult:
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
    if result.returncode != 0:
        output = f"{output}\n[exit code: {result.returncode}]".strip()
    return CommandResult(output=output, returncode=result.returncode)


class BuddyApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry("560x420")
        self.last_prompt_text = ""

        self.status_var = tk.StringVar(value="Codex Harness Buddy")
        tk.Label(root, textvariable=self.status_var, anchor="w").pack(fill="x", padx=8, pady=(8, 4))

        self.buddy_state_var = tk.StringVar(value=buddy_state_label("대기 중"))
        tk.Label(root, textvariable=self.buddy_state_var, anchor="w").pack(fill="x", padx=8, pady=(0, 4))

        for group_label, button_labels in BUTTON_GROUPS:
            group_frame = tk.Frame(root)
            group_frame.pack(fill="x", padx=8, pady=2)
            tk.Label(group_frame, text=group_label, width=8, anchor="w").pack(side="left")
            for label in button_labels:
                args = BUTTON_COMMANDS[label]
                tk.Button(
                    group_frame,
                    text=label,
                    command=lambda button_label=label, command_args=args: self.run_and_show(command_args, button_label),
                ).pack(side="left", padx=3)

        input_frame = tk.Frame(root)
        input_frame.pack(fill="x", padx=8, pady=4)
        self.nudge_entry = tk.Entry(input_frame)
        self.nudge_entry.pack(side="left", fill="x", expand=True)
        tk.Button(input_frame, text="Nudge", command=self.run_nudge).pack(side="left", padx=(6, 0))
        tk.Button(input_frame, text=COPY_BUTTON_LABEL, command=self.copy_output).pack(side="left", padx=(6, 0))
        tk.Button(input_frame, text=COPY_PROMPT_BUTTON_LABEL, command=self.copy_prompt).pack(side="left", padx=(6, 0))

        self.output = scrolledtext.ScrolledText(root, wrap="word", height=16)
        self.output.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self.run_and_show(["status"], "Status")

    def append_output(self, header: str, output: str) -> None:
        if self.output.get("1.0", tk.END).strip():
            self.output.insert(tk.END, "\n\n")
        self.output.insert(tk.END, header)
        self.output.insert(tk.END, output or "(출력 없음)")
        self.output.see(tk.END)

    def run_and_show(self, args: list[str], source_label: str) -> None:
        self.status_var.set(running_status(args))
        self.root.update_idletasks()
        result = run_buddy_command(args)
        buddy_state = buddy_state_after(source_label, result.returncode)
        self.status_var.set(completed_status(args, result.returncode))
        self.buddy_state_var.set(buddy_state_label(buddy_state))
        if should_keep_prompt(args, result.returncode):
            self.last_prompt_text = result.output
        elif should_clear_prompt(args, result.returncode):
            self.clear_prompt()
        self.append_output(output_header(source_label, args, buddy_state), result.output)

    def run_nudge(self) -> None:
        user_input = self.nudge_entry.get().strip()
        if not user_input:
            return
        args = ["nudge", user_input]
        self.status_var.set(running_status(["nudge"]))
        self.root.update_idletasks()
        result = run_buddy_command(args)
        buddy_state = buddy_state_after("Nudge", result.returncode)
        self.status_var.set(completed_status(["nudge"], result.returncode))
        self.buddy_state_var.set(buddy_state_label(buddy_state))
        if should_clear_prompt(args, result.returncode):
            self.clear_prompt()
        self.append_output(nudge_header(user_input, buddy_state), result.output)

    def copy_output(self) -> None:
        text = clipboard_text(self.output.get("1.0", tk.END))
        if not text:
            self.status_var.set("복사할 출력이 없습니다")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status_var.set(copy_status())

    def clear_clipboard(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(cleared_clipboard_text())
        self.root.update()

    def clear_prompt(self) -> None:
        self.last_prompt_text = ""
        if missing_prompt_should_clear_clipboard():
            self.clear_clipboard()

    def copy_prompt(self) -> None:
        text = clipboard_text(self.last_prompt_text)
        if not text:
            if missing_prompt_should_clear_clipboard():
                self.clear_clipboard()
            self.status_var.set(missing_prompt_status())
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status_var.set(copy_prompt_status())


def main() -> int:
    root = tk.Tk()
    BuddyApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
