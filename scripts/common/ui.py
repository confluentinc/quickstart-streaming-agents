"""
User interface utilities for interactive prompts.

Provides functions for:
- Multi-choice selection prompts
- Text input with default values
- Consistent user interaction patterns
"""

import getpass
import re
import sys
from typing import List


def prompt_choice(prompt_text: str, options: List[str]) -> str:
    """
    Prompt user to select from numbered options.

    Args:
        prompt_text: Question or instruction to display
        options: List of options to choose from

    Returns:
        Selected option string
    """
    print(f"\n{prompt_text}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        choice = input(f"\nEnter choice (1-{len(options)}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print(f"Invalid choice. Please enter a number between 1 and {len(options)}.")


def prompt_with_default(prompt_text: str, default: str = "", secret: bool = False) -> str:
    """
    Prompt user with optional default value.

    If a default is provided and the user enters nothing, the default is returned.
    If no default is provided, the prompt repeats until a value is entered.
    With ``secret=True`` the default is shown masked and typed/pasted input is
    echoed as ``*``.

    Args:
        prompt_text: Question or instruction to display
        default: Default value to use if user enters nothing
        secret: Mask the default and echo input as ``*``

    Returns:
        User input or default value
    """
    read = prompt_secret if secret else input
    if default:
        if secret:
            display_default = mask_secret(default)
        else:
            display_default = default if len(default) <= 50 else default[:47] + "..."
        value = read(f'{prompt_text} [current: "{display_default}"]: ').strip()
        return value if value else default
    else:
        value = read(f"{prompt_text}: ").strip()
        while not value:
            print("This field is required.")
            value = read(f"{prompt_text}: ").strip()
        return value


# Names whose values are secrets. API key *IDs* (Confluent, AWS access key) are
# deliberately not matched: they are identifiers, safe to show in full.
_SECRET_NAME_RE = re.compile(r"secret|passw(or)?d|token|openai_api_key", re.IGNORECASE)


def is_secret_name(name: str) -> bool:
    """True if a credential/env var name refers to a secret value."""
    return bool(_SECRET_NAME_RE.search(name))


def mask_secret(value: str, keep: int = 4) -> str:
    """Mask a secret, keeping the first and last ``keep`` characters.

    Values too short to hide anything behind those edges are fully masked.
    The mask keeps the original length so the user can tell a paste landed.
    """
    if not value:
        return ""
    if len(value) < keep * 4:
        return "*" * len(value)
    return value[:keep] + "*" * (len(value) - 2 * keep) + value[-keep:]


def display_value(name: str, value: str) -> str:
    """Value as it should appear on screen: masked if ``name`` is a secret."""
    return mask_secret(value) if is_secret_name(name) else value


def prompt_secret(prompt_text: str) -> str:
    """Read a secret, echoing ``*`` per character instead of the text.

    Falls back to ``getpass`` (no echo) when stdin/stdout is not a terminal.
    """
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return getpass.getpass(prompt_text)

    sys.stdout.write(prompt_text)
    sys.stdout.flush()
    chars: List[str] = []

    def handle(ch: str) -> bool:
        """Apply one keystroke; return True when input is finished."""
        if ch in ("\r", "\n"):
            return True
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch == "\x04":
            if not chars:
                raise EOFError
            return True
        if ch in ("\x7f", "\x08"):
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
        elif ch.isprintable():
            chars.append(ch)
            sys.stdout.write("*")
        sys.stdout.flush()
        return False

    try:
        import msvcrt  # Windows

        while True:
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):  # arrow/function key: discard its second code
                msvcrt.getwch()
                continue
            if handle(ch):
                break
    except ImportError:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)  # keeps Ctrl-C working; no echo, no line buffering
            while True:
                if handle(sys.stdin.read(1)):
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    finally:
        sys.stdout.write("\n")
        sys.stdout.flush()
    return "".join(chars)
