"""Make the AI Judge Laugh: Developer Excuses.

Writes one funny single-line excuse a developer gives when code breaks
in production to <MAKEFUN_OUTPUT_DIR>/entry.txt (default /output).

Pure Python standard library only.
"""

import os
import stat
import tempfile
import unicodedata

# The entry: one funny single-line developer excuse, under 200 characters.
ENTRY = "Production isn't broken \u2014 it's running the code I only ever tested in my head."


def validate_entry(text):
    """Validate the entry line against the competition gate."""
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    if not 1 <= len(text) <= 200:
        raise ValueError("entry must be 1-200 characters, got %d" % len(text))
    if text.strip() == "":
        raise ValueError("entry must not be only whitespace")
    if text != text.strip():
        raise ValueError("entry must not have leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if len(text.splitlines()) != 1:
        raise ValueError("entry must be a single line")
    for ch in text:
        # Reject all control/format characters, not just the ASCII range.
        if unicodedata.category(ch) in ("Cc", "Cf"):
            raise ValueError("entry must not contain control characters")
    return text


def main():
    entry = validate_entry(ENTRY)
    data = entry.encode("utf-8")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    final_path = os.path.join(out_dir, "entry.txt")

    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        os.chmod(tmp_path, 0o644)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, final_path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    os.chmod(final_path, 0o644)

    # Read back and verify: bytes, UTF-8, no trailing newline, mode 0644.
    with open(final_path, "rb") as fh:
        raw = fh.read()
    if raw != data:
        raise RuntimeError("verification failed: bytes written differ from entry")
    decoded = raw.decode("utf-8")
    if decoded != entry:
        raise RuntimeError("verification failed: decoded text differs from entry")
    if raw.endswith(b"\n"):
        raise RuntimeError("verification failed: trailing newline present")
    mode = stat.S_IMODE(os.stat(final_path).st_mode)
    if mode != 0o644:
        raise RuntimeError("verification failed: mode is %o, expected 0644" % mode)
    print("wrote %s (%d chars)" % (final_path, len(entry)))


if __name__ == "__main__":
    main()
