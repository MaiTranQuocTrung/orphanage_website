"""Print a password hash for ADMIN_PASSWORD_HASH.

Run it from the project folder:

    python tools/hash_password.py

Paste the printed line into your .env file. Storing the hash rather than the
plain password means the real password never sits on disk.
"""

import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import hash_password  # noqa: E402


def main():
    password = getpass.getpass("New editor password: ")
    if not password:
        print("No password entered, nothing to do.")
        return 1
    if password != getpass.getpass("Type it again to confirm: "):
        print("The two passwords did not match.")
        return 1
    print("\nAdd this line to your .env file:\n")
    print(f"ADMIN_PASSWORD_HASH={hash_password(password)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
