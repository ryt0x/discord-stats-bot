"""
Stats cog — provides the /stats slash command.
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import store
from config import TOP_CHANNELS_LIMIT, TOP_USERS_LIMIT
from utils.embeds import build_stats_embed


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="stats", description="Show today's server activity at a glance.")
    @app_commands.guild_only()
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        embed = await build_stats_embed(
            guild=guild,
            top_users=store.get_top_users(guild.id, TOP_USERS_LIMIT),
            top_channels=store.get_top_channels(guild.id, TOP_CHANNELS_LIMIT),
            total_messages=store.get_total_messages(guild.id),
            active_users=store.get_active_users(guild.id),
            peak_hour=store.get_peak_hour(guild.id),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
