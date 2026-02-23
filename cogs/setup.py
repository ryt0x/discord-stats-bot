"""
Setup cog — /setup command for admins to configure the bot.
"""

import discord
from discord import app_commands
from discord.ext import commands

import store


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setup",
        description="Set the channel where daily summaries will be posted.",
    )
    @app_commands.describe(channel="The channel to post daily summaries in (defaults to this channel).")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
    ):
        target = channel or interaction.channel
        store.stats_channels[interaction.guild.id] = target.id
        store.save_config()

        embed = discord.Embed(
            title="✅ Setup Complete",
            description=f"Daily summaries will be posted in {target.mention}.",
            color=discord.Color.green(),
        )
        embed.set_footer(text="Use /stats anytime to see current activity.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="setup-clear",
        description="Stop posting daily summaries and clear the configured stats channel.",
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_clear(self, interaction: discord.Interaction):
        if interaction.guild.id not in store.stats_channels:
            await interaction.response.send_message(
                "ℹ️ No stats channel is configured — nothing to clear.",
                ephemeral=True,
            )
            return

        del store.stats_channels[interaction.guild.id]
        store.save_config()

        embed = discord.Embed(
            title="🗑️ Setup Cleared",
            description="Daily summaries have been disabled. Run `/setup` again to re-enable.",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @setup_clear.error
    async def setup_clear_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You need the **Manage Server** permission to run this command.",
                ephemeral=True,
            )
        else:
            raise error

    @setup.error
    async def setup_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You need the **Manage Server** permission to run this command.",
                ephemeral=True,
            )
        else:
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))