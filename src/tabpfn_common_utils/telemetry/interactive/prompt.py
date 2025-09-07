"""Prompt management for telemetry."""

from __future__ import annotations

import html
import logging
import queue
import re
import textwrap
import threading
from dataclasses import dataclass
from typing import Literal

# Logging
_logger = logging.getLogger(__name__)

# Outcome of a prompt
Outcome = Literal["accepted", "declined", "dismissed", "timeout"]

# Jupyter notebook template HTML code
_JUPYTER_HTML = """
<div style="
    border:1px solid #e5e7eb;border-radius:10px;padding:12px;margin:6px 0;
    font-family:system-ui, -apple-system, Segoe UI, Roboto, Helvetica, sans-serif;">
  <div style="font-weight:600;margin-bottom:6px;">{title}</div>
  <div style="white-space:pre-line;margin-bottom:6px;">{body}</div>
  <div style="white-space:pre-line;margin-bottom:8px;color:#4b5563;">{hint}</div>
  <div style="margin-top:8px;">
    <a href="https://priorlabs.ai/privacy_policy/" target="_blank"
        style="color:#3b82f6;text-decoration:none;font-size:14px;"
    >Privacy Policy</a>
  </div>
</div>
"""


@dataclass(frozen=True)
class EmailPromptResult:
    """Result of an email prompt."""

    outcome: Outcome
    email: str | None = None


def get_default_prompt() -> tuple[str, str, str]:
    """Get the default prompt.

    Returns:
        A tuple containing the prompt title, body, and hint.
    """
    # Prompt title
    title = "📬 Stay in the loop? (Optional)"

    # Prompt body
    body = textwrap.dedent("""\
        Thank you for using TabPFN! We'd love to keep you updated on TabPFN news:
        • Major releases
        • Critical bug fixes
        • Research highlights
    """)

    # Prompt hint
    hint = textwrap.dedent("""\
        Enter your email (optional) and press Enter. Leave blank to skip.
        We'll store it securely, use it only for these updates, and never share it.
        You can opt out anytime.
    """)

    return title, body, hint


def prompt_email_ipython(title: str, body: str, hint: str) -> EmailPromptResult:
    """Blocking IPython prompt: renders info, then waits for input().

    Args:
        title: The title of the prompt.
        body: The body of the prompt.
        hint: The hint of the prompt.

    Returns:
        A EmailPromptResult object.
    """
    try:
        # Optionally use IPython.display.display and HTML, depending on runtime
        from IPython.display import HTML, display  # type: ignore

        # Format the text to show to the user
        text = _JUPYTER_HTML.format(
            title=html.escape(title),
            body=html.escape(body),
            hint=html.escape(hint),
        )

        display(HTML(text))
    except Exception:  # noqa: BLE001
        # If rich display fails, continue with a plain text prompt as in TTY
        return prompt_email_tty(title, body, hint)

    return _trigger_input_prompt(blocking=True)


def prompt_email_tty(title: str, body: str, hint: str) -> EmailPromptResult:
    """Blocking TTY prompt: displays text and waits for input() in terminal.

    Args:
        title: The title of the prompt.
        body: The body of the prompt.
        hint: The hint of the prompt.

    Returns:
        A EmailPromptResult object.
    """
    # Display the prompt in terminal
    print(f"\n{title}")  # noqa: T201
    print(f"{body}")  # noqa: T201
    print(f"{hint}\n")  # noqa: T201
    print("Privacy Policy: https://priorlabs.ai/privacy_policy/\n")  # noqa: T201

    return _trigger_input_prompt(blocking=False, timeout=15)


def _input_worker(q: queue.Queue[str | None]) -> None:
    """Worker that reads a single line from stdin and communicates via queue.

    Args:
        q: The queue to communicate via.
    """
    try:
        raw = input("Email (optional, press Enter to skip): ").strip()
        q.put(raw)
    except Exception:  # noqa: BLE001
        q.put(None)


def _trigger_input_prompt(
    blocking: bool = True,  # noqa: FBT001 FBT002
    timeout: int = 30,
) -> EmailPromptResult:
    """Trigger the input prompt.

    Args:
        blocking: Whether to block forever or up to `timeout` seconds.
        timeout: The timeout in seconds.

    Returns:
        A EmailPromptResult object.
    """
    q: queue.Queue[str | None] = queue.Queue()
    t = threading.Thread(target=_input_worker, args=(q,), daemon=True)
    t.start()

    try:
        # Block forever or up to timeout seconds (TTY)
        t.join(None if blocking else timeout)
    except KeyboardInterrupt:
        return EmailPromptResult("dismissed")

    if t.is_alive():
        # No activity within timeout
        return EmailPromptResult("timeout")

    try:
        raw = q.get_nowait()
    except queue.Empty:
        return EmailPromptResult("dismissed")

    # No input provided
    if not raw:
        return EmailPromptResult("dismissed")

    # Invalid email address
    if not _is_valid_email(raw):
        return EmailPromptResult("declined")

    return EmailPromptResult("accepted", email=raw)


def _is_valid_email(text: str) -> bool:
    """Check if text looks like a valid email address.

    Args:
        text: The text to check.

    Returns:
        True if the text looks like an email address, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, text))
