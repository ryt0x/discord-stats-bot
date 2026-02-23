# 📊 Discord Stats Bot

A lightweight Discord bot that tracks message activity in your server and surfaces at-a-glance insights — no external dashboards or databases required.

---

## Features (MVP)

| Feature | Details |
|---|---|
| **Activity tracking** | Counts messages per user and per channel, resets daily at midnight UTC |
| **`/stats`** | Shows an embed with top users, top channels, total messages, active members, and peak hour |
| **Daily summary** | Automatically posts a summary embed at a configurable UTC hour |
| **`/setup`** | Lets admins pick which channel receives daily summaries |

---

# 📊 Discord Stats Bot

A small, easy-to-run Discord bot that tracks daily message activity and posts simple summaries — no external database required.

---

## Overview

- Tracks messages per-user and per-channel for each guild.
- Provides a `/stats` command for an at-a-glance leaderboard and summary.
- Posts a configurable daily summary embed to a designated channel.

This repository is focused on reliability and minimal setup for self-hosting.

---

## Features

- Message counting (per-user, per-channel) with daily reset at UTC midnight
- `/stats` slash command (shows top users/channels, totals, peak hour)
- `/setup` slash command (admin-only) to set the daily summary channel
- Configurable daily summary hour via environment variable

---

## Repository Layout

```
bot.py               # Entry point — creates the bot and loads cogs
config.py            # Configuration loader (env + defaults)
store.py             # In-memory counters + persistence for guild config
requirements.txt
.env.example
data/                # runtime data (e.g. data/config.json)
cogs/                # cog implementations
    ├─ tracker.py       # message event listeners
    ├─ stats.py         # /stats command
    ├─ setup.py         # /setup command
    └─ summary.py       # daily summary task
utils/
    └─ embeds.py        # helpers to build Discord embeds
```

---

## Quick Start

1. Clone the repo and create a virtual environment

```bash
git clone github.com/ryt0x/discord-stats-bot  
cd "discord-stats-bot"
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a Discord application and bot

- Visit https://discord.com/developers/applications and create an application.
- Add a bot user under **Bot** and copy the token.
- Enable **Message Content Intent** and **Server Members Intent** if you want richer tracking.

3. Invite the bot to your server

- Use the OAuth2 URL Generator with scopes `bot` and `applications.commands`.
- Typical permissions: `View Channels`, `Send Messages`, `Embed Links`, `Read Message History`.

4. Configure environment variables

```bash
copy .env.example .env
```

Edit `.env` and set `DISCORD_BOT_TOKEN` and `DAILY_SUMMARY_UTC_HOUR` (0–23).

5. Run the bot

```bash
python bot.py
```

---

## Commands

- `/stats` — visible to everyone; shows today's leaderboard and stats.
- `/setup [channel]` — admin-only (Manage Server) command to set the daily summary channel.
 - `/setup-clear` — admin-only (Manage Server) command to stop posting daily summaries and clear the configured stats channel.

---

## Data & Persistence

- Message counts are kept in memory and reset each UTC day.
- Guild configuration (summary channel) is saved to `data/config.json` so it persists across restarts.
- If you need historical persistence, consider adding SQLite or another lightweight DB and migrating `store.py`.

---

## Configuration Options

Key config values live in `.env` or `config.py`.

- `DISCORD_BOT_TOKEN` (required) — your bot token.
- `DAILY_SUMMARY_UTC_HOUR` (default: `0`) — UTC hour to post daily summary.
- `TOP_USERS_LIMIT` (default: `10`) — number of users in leaderboards.

---

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repo.
2. Create a feature branch.
3. Open a PR with a clear description and testing steps.

Please keep changes focused and follow the existing code style.

---
