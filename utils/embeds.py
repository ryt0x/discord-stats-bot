"""
Shared embed builder used by both the /stats command and the daily summary task.
"""

from __future__ import annotations

from datetime import datetime, timezone

import discord


def _bar(value: int, max_value: int, length: int = 10) -> str:
    """Return a simple text progress bar."""
    if max_value == 0:
        filled = 0
    else:
        filled = round((value / max_value) * length)
    return "█" * filled + "░" * (length - filled)


def _format_hour(hour: int) -> str:
    """Convert a UTC hour int to a readable string like '3 PM UTC'."""
    suffix = "AM" if hour < 12 else "PM"
    display = hour % 12 or 12
    return f"{display} {suffix} UTC"


async def build_stats_embed(
    *,
    guild: discord.Guild,
    top_users: list[tuple[int, int]],
    top_channels: list[tuple[int, int]],
    total_messages: int,
    active_users: int,
    peak_hour: int | None,
    is_daily_summary: bool = False,
) -> discord.Embed:
    title = (
        f"📊 Daily Summary — {guild.name}"
        if is_daily_summary
        else f"📊 Today's Activity — {guild.name}"
    )

    embed = discord.Embed(
        title=title,
        color=discord.Color.blurple(),
        timestamp=datetime.now(timezone.utc),
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    # ── Overview ──────────────────────────────────────────────────────────── #
    overview_lines = [
        f"💬 **Total messages:** {total_messages:,}",
        f"👥 **Active members:** {active_users:,}",
    ]
    if peak_hour is not None:
        overview_lines.append(f"⏰ **Peak hour:** {_format_hour(peak_hour)}")

    embed.add_field(name="Overview", value="\n".join(overview_lines), inline=False)

    # ── Top Users ─────────────────────────────────────────────────────────── #
    if top_users:
        max_msgs = top_users[0][1] if top_users else 1
        user_lines = []
        medals = ["🥇", "🥈", "🥉"]

        for i, (user_id, count) in enumerate(top_users):
            medal = medals[i] if i < 3 else f"`{i + 1}.`"
            member = guild.get_member(user_id)
            name = member.display_name if member else f"User {user_id}"
            bar = _bar(count, max_msgs)
            user_lines.append(f"{medal} **{name}** — {count:,} msgs\n{bar}")

        embed.add_field(
            name=f"🏆 Top {len(top_users)} Users",
            value="\n".join(user_lines) or "No data yet.",
            inline=False,
        )
    else:
        embed.add_field(name="🏆 Top Users", value="No messages recorded yet.", inline=False)

    # ── Top Channels ──────────────────────────────────────────────────────── #
    if top_channels:
        max_ch = top_channels[0][1] if top_channels else 1
        ch_lines = []

        for channel_id, count in top_channels:
            channel = guild.get_channel(channel_id)
            ch_name = f"<#{channel_id}>" if channel else f"Channel {channel_id}"
            bar = _bar(count, max_ch, length=8)
            ch_lines.append(f"{ch_name} — {count:,} msgs  {bar}")

        embed.add_field(
            name=f"📢 Top {len(top_channels)} Channels",
            value="\n".join(ch_lines),
            inline=False,
        )
    else:
        embed.add_field(name="📢 Top Channels", value="No messages recorded yet.", inline=False)

    embed.set_footer(text="Stats reset daily at midnight UTC • Use /stats to refresh")
    return embed
