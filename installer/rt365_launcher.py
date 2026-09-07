"""PyInstaller entry point for the one-file ``rt365`` executable (see installer/rt365.spec)."""

from __future__ import annotations

import multiprocessing
import sys

from rt365_cli.main import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.exit(main())
