"""
Tracker cog — passively listens to every message and records it in the store.
"""

import discord
from discord.ext import commands

import store


class Tracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore DMs, bot messages, and system messages
        if not message.guild or message.author.bot or not isinstance(message.author, discord.Member):
            return

        store.record_message(
            guild_id=message.guild.id,
            user_id=message.author.id,
            channel_id=message.channel.id,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Tracker(bot))
