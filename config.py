import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "!")

if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set. Add it to your .env file.")

# UTC hour (0-23) at which the daily summary is posted
DAILY_SUMMARY_UTC_HOUR: int = int(os.getenv("DAILY_SUMMARY_UTC_HOUR", "0"))

# Max entries shown in top-users / top-channels lists
TOP_USERS_LIMIT: int = 10
TOP_CHANNELS_LIMIT: int = 5
