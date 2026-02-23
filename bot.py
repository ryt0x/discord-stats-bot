import discord
from discord.ext import commands
import asyncio
import logging
from config import BOT_TOKEN, COMMAND_PREFIX
import store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bot")

COGS = [
    "cogs.tracker",
    "cogs.stats",
    "cogs.setup",
    "cogs.summary",
]


class StatsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")

        await self.tree.sync()
        logger.info("Slash commands synced.")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="server activity 📊",
            )
        )


async def main():
    bot = StatsBot()
    # Load persisted guild config into memory before cogs initialize
    store.load_config()

    @bot.command()
    @commands.is_owner()
    async def sync(ctx: commands.Context):
        await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send("✅ Synced to this guild.")

    async with bot:
        await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())