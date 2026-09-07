"""Kill Switch service [Source: 02, 05, 10; P4].

Six levels; activation unilateral by any authorised human role or runtime monitor; deactivation
by two persons from different lines with a logged reason. Agents are denied and alerted.
Protected path: Chief Risk Agent CODEOWNER approval required.
"""

from killswitch_service.service import Activation, KillSwitchHooks, KillSwitchLevel, KillSwitchService

__all__ = ["KillSwitchService", "KillSwitchLevel", "Activation", "KillSwitchHooks"]
