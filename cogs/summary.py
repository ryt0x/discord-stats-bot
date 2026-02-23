"""
Summary cog — posts an automatic daily summary at a configured UTC hour.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks

import store
from config import DAILY_SUMMARY_UTC_HOUR, TOP_CHANNELS_LIMIT, TOP_USERS_LIMIT
from utils.embeds import build_stats_embed

logger = logging.getLogger("summary")


class Summary(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_summary_date: dict[int, int] = {}  # guild_id -> day-of-year
        self.daily_summary_loop.start()

    def cog_unload(self):
        self.daily_summary_loop.cancel()

    @tasks.loop(minutes=1)
    async def daily_summary_loop(self):
        now = datetime.now(timezone.utc)
        if now.hour != DAILY_SUMMARY_UTC_HOUR or now.minute != 0:
            return

        for guild in self.bot.guilds:
            # Ensure we only post once per day per guild
            day_key = now.timetuple().tm_yday
            if self._last_summary_date.get(guild.id) == day_key:
                continue
            self._last_summary_date[guild.id] = day_key

            await self._post_summary(guild)
            store.reset_guild(guild.id)

    @daily_summary_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    async def _post_summary(self, guild: discord.Guild) -> None:
        channel_id = store.stats_channels.get(guild.id)
        if not channel_id:
            logger.info(f"No stats channel configured for guild {guild.id}, skipping summary.")
            return

        channel = guild.get_channel(channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            logger.warning(f"Stats channel {channel_id} not found in guild {guild.id}.")
            return

        embed = await build_stats_embed(
            guild=guild,
            top_users=store.get_previous_top_users(guild.id, TOP_USERS_LIMIT),
            top_channels=store.get_previous_top_channels(guild.id, TOP_CHANNELS_LIMIT),
            total_messages=store.get_previous_total_messages(guild.id),
            active_users=store.get_previous_active_users(guild.id),
            peak_hour=store.get_previous_peak_hour(guild.id),
            is_daily_summary=True,
        )

        try:
            await channel.send(embed=embed)
            logger.info(f"Posted daily summary for guild {guild.id} in channel {channel_id}.")
        except discord.Forbidden:
            logger.warning(f"Missing permissions to post in channel {channel_id} (guild {guild.id}).")


async def setup(bot: commands.Bot):
    await bot.add_cog(Summary(bot))
