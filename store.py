"""
In-memory storage for the stats bot.

Layout
------
message_counts[guild_id][user_id]       -> int   (messages today)
channel_counts[guild_id][channel_id]    -> int   (messages today)
hourly_counts[guild_id][hour (0-23)]    -> int   (messages today per UTC hour)
stats_channels[guild_id]                -> int   (channel id for daily summary)
last_reset[guild_id]                    -> date  (date of last counter reset)
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import date, datetime, timezone, timedelta
from config import DAILY_SUMMARY_UTC_HOUR
from typing import DefaultDict

# --------------------------------------------------------------------------- #
# Live counters (reset daily)                                                  #
# --------------------------------------------------------------------------- #

message_counts: DefaultDict[int, DefaultDict[int, int]] = defaultdict(
    lambda: defaultdict(int)
)
channel_counts: DefaultDict[int, DefaultDict[int, int]] = defaultdict(
    lambda: defaultdict(int)
)
hourly_counts: DefaultDict[int, DefaultDict[int, int]] = defaultdict(
    lambda: defaultdict(int)
)
last_reset: dict[int, date] = {}

# --------------------------------------------------------------------------- #
# Previous day snapshots (captured at midnight before reset)                   #
# --------------------------------------------------------------------------- #

previous_message_counts: DefaultDict[int, DefaultDict[int, int]] = defaultdict(
    lambda: defaultdict(int)
)
previous_channel_counts: DefaultDict[int, DefaultDict[int, int]] = defaultdict(
    lambda: defaultdict(int)
)
previous_hourly_counts: DefaultDict[int, DefaultDict[int, int]] = defaultdict(
    lambda: defaultdict(int)
)

# --------------------------------------------------------------------------- #
# Persistent config (written to disk as JSON)                                  #
# --------------------------------------------------------------------------- #

_CONFIG_PATH = "data/config.json"
stats_channels: dict[int, int] = {}  # guild_id -> channel_id


def _ensure_data_dir() -> None:
    os.makedirs("data", exist_ok=True)


def load_config() -> None:
    """Load persisted guild config from disk."""
    global stats_channels
    _ensure_data_dir()
    if os.path.exists(_CONFIG_PATH):
        with open(_CONFIG_PATH, "r") as f:
            raw = json.load(f)
        stats_channels = {int(k): int(v) for k, v in raw.get("stats_channels", {}).items()}


def save_config() -> None:
    """Persist guild config to disk."""
    _ensure_data_dir()
    with open(_CONFIG_PATH, "w") as f:
        json.dump({"stats_channels": {str(k): v for k, v in stats_channels.items()}}, f, indent=2)


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

def record_message(guild_id: int, user_id: int, channel_id: int) -> None:
    """Increment all relevant counters for a new message."""
    _auto_reset(guild_id)
    message_counts[guild_id][user_id] += 1
    channel_counts[guild_id][channel_id] += 1
    hour = datetime.now(timezone.utc).hour
    hourly_counts[guild_id][hour] += 1


def snapshot_and_reset(guild_id: int) -> None:
    """Snapshot current counters to 'previous_' dicts, then reset current counters."""
    # Save current counters as previous day's data
    previous_message_counts[guild_id] = message_counts[guild_id].copy()
    previous_channel_counts[guild_id] = channel_counts[guild_id].copy()
    previous_hourly_counts[guild_id] = hourly_counts[guild_id].copy()
    
    # Clear current counters
    message_counts[guild_id].clear()
    channel_counts[guild_id].clear()
    hourly_counts[guild_id].clear()
    
    # Update reset timestamp
    now = datetime.now(timezone.utc)
    last_reset[guild_id] = (now - timedelta(hours=DAILY_SUMMARY_UTC_HOUR)).date()


def _auto_reset(guild_id: int) -> None:
    """Reset counters if the UTC date has rolled over."""
    now = datetime.now(timezone.utc)
    # Align the day boundary with the configured daily summary hour so
    # counters are reset only after the scheduled summary has run.
    shifted_day = (now - timedelta(hours=DAILY_SUMMARY_UTC_HOUR)).date()
    if last_reset.get(guild_id) != shifted_day:
        snapshot_and_reset(guild_id)


def reset_guild(guild_id: int) -> None:
    """Force-reset all counters for a guild (called by the daily summary task)."""
    snapshot_and_reset(guild_id)


def get_total_messages(guild_id: int) -> int:
    return sum(message_counts[guild_id].values())


def get_active_users(guild_id: int) -> int:
    return len(message_counts[guild_id])


def get_top_users(guild_id: int, limit: int = 10) -> list[tuple[int, int]]:
    """Returns [(user_id, count), ...] sorted descending."""
    return sorted(message_counts[guild_id].items(), key=lambda x: x[1], reverse=True)[:limit]


def get_top_channels(guild_id: int, limit: int = 5) -> list[tuple[int, int]]:
    """Returns [(channel_id, count), ...] sorted descending."""
    return sorted(channel_counts[guild_id].items(), key=lambda x: x[1], reverse=True)[:limit]


def get_peak_hour(guild_id: int) -> int | None:
    """Returns the UTC hour with the most messages, or None if no data."""
    counts = hourly_counts[guild_id]
    if not counts:
        return None
    return max(counts, key=lambda h: counts[h])


def get_previous_total_messages(guild_id: int) -> int:
    """Returns total messages from the previous day's snapshot."""
    return sum(previous_message_counts[guild_id].values())


def get_previous_active_users(guild_id: int) -> int:
    """Returns active users from the previous day's snapshot."""
    return len(previous_message_counts[guild_id])


def get_previous_top_users(guild_id: int, limit: int = 10) -> list[tuple[int, int]]:
    """Returns [(user_id, count), ...] from previous day, sorted descending."""
    return sorted(previous_message_counts[guild_id].items(), key=lambda x: x[1], reverse=True)[:limit]


def get_previous_top_channels(guild_id: int, limit: int = 5) -> list[tuple[int, int]]:
    """Returns [(channel_id, count), ...] from previous day, sorted descending."""
    return sorted(previous_channel_counts[guild_id].items(), key=lambda x: x[1], reverse=True)[:limit]


def get_previous_peak_hour(guild_id: int) -> int | None:
    """Returns the UTC hour with the most messages from previous day, or None if no data."""
    counts = previous_hourly_counts[guild_id]
    if not counts:
        return None
    return max(counts, key=lambda h: counts[h])
