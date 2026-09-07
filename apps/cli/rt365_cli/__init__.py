"""``rt365`` — command-line entry point of the dev/sim distribution [Source: 16; ADR-016].

The same binary serves the dashboard/BFF, runs the self-check and synthetic probe, exposes the MCP stdio
tool server and runs the broker certification harness. It carries the dev/sim posture with it: an
unlabelled environment fails closed, only ``sim`` can be served, the fixture registry is refused anywhere else.
"""

from importlib import metadata

try:
    __version__ = metadata.version("rt365-robotrader")
except metadata.PackageNotFoundError:  # frozen bundle or source tree without an install
    __version__ = "0.1.0"

__all__ = ["__version__"]
