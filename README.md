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

## Project Structure

```
discord-stats-bot/
├── bot.py              # Entry point — creates the bot and loads cogs
├── config.py           # Loads settings from .env
├── store.py            # In-memory counters + lightweight JSON config persistence
├── requirements.txt
├── .env.example
├── cogs/
│   ├── tracker.py      # Listens to messages and records them in the store
│   ├── stats.py        # /stats slash command
│   ├── setup.py        # /setup slash command (admin only)
│   └── summary.py      # Background task that posts the daily summary
└── utils/
    └── embeds.py       # Shared embed builder (used by /stats and the daily summary)
```

---

## Quick Start

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd discord-stats-bot
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create a Discord application and bot

1. Go to <https://discord.com/developers/applications> and create a **New Application**.
2. Navigate to **Bot** → click **Add Bot**.
3. Under **Token**, click **Reset Token** and copy it.
4. Under **Privileged Gateway Intents**, enable:
   - **Server Members Intent**
   - **Message Content Intent**

### 3. Invite the bot to your server

Use the **OAuth2 → URL Generator** in the developer portal:

- **Scopes:** `bot`, `applications.commands`
- **Bot Permissions:** `Read Messages/View Channels`, `Send Messages`, `Embed Links`

Open the generated URL and add the bot to your server.

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DISCORD_BOT_TOKEN=your-token-here
DAILY_SUMMARY_UTC_HOUR=0       # 0 = midnight UTC; change to e.g. 9 for 9 AM UTC
```

### 5. Run the bot

```bash
python bot.py
```

---

## Commands

| Command | Who can use it | Description |
|---|---|---|
| `/stats` | Everyone | Shows today's activity summary |
| `/setup [channel]` | Admins (Manage Server) | Sets the channel for daily summaries |

---

## How data is stored

- **Message counts** live in memory and reset automatically each UTC day.
- **Guild config** (the stats channel you set with `/setup`) is written to `data/config.json` so it survives bot restarts.
- No database is required. If you want persistence across restarts for message counts, that's a natural next step (SQLite is recommended).

---

## Customisation

All tuneable values live in `.env` or `config.py`:

| Variable | Default | Description |
|---|---|---|
| `DISCORD_BOT_TOKEN` | — | **Required.** Your bot token. |
| `COMMAND_PREFIX` | `!` | Prefix for legacy text commands. |
| `DAILY_SUMMARY_UTC_HOUR` | `0` | UTC hour to post daily summary (0–23). |
| `TOP_USERS_LIMIT` | `10` | Max users shown in the leaderboard. |
| `TOP_CHANNELS_LIMIT` | `5` | Max channels shown in the summary. |

---

## Roadmap (post-MVP ideas)

- [ ] SQLite persistence for historical trends
- [ ] Weekly/monthly reports
- [ ] Emoji bar charts or image-based charts
- [ ] Per-user privacy opt-out
- [ ] Custom time zones per guild
- [ ] Web dashboard export
