import datetime
import logging
import asyncio
import os
import time
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from discord import Intents, utils, Bot
from discord.ext import tasks
from utils import recovery_birthday
from constants import (
    TARGETED_HOUR_BIRTHDAY_REMINDER,
    DEFAULT_BIRTHDAY_WISHING_SENTENCE,
    DEFAULT_FIRSTNAME_KEY,
    DEFAULT_NAME_KEY,
    IUT_SERV_ID,
    DEFAULT_GENERAL_CHANNEL,
    DEFAULT_TIMEZONE,
    DEFAULT_CELEBRITE_KEY
)
from _Token import TOKEN


intents = Intents.default()
bot: Bot = Bot(intents=intents)


@bot.event
async def on_ready():
    """Actions to do when the bot is ready to use"""
    if not bot.user:
        raise InterruptedError("Cannot connect")

    logger_main.info(
        "Logged in as %s (%s)", bot.user.name, bot.user.id
    )  # Bot connection confirmation

    await wait_for_auto_start_birthday_reminder()


async def wait_for_auto_start_birthday_reminder():
    """Wait the indicated time to start the birthay_reminder loop
    Args:
        current_time (datetime): Current time DEFAULT datetime.datetime.now()
        target_time (datetime): Time targeted (year/month/day/hour/min/second)
    """
    current_time: datetime.datetime = datetime.datetime.now()
    target_time: datetime.datetime = datetime.datetime(
        current_time.year,
        current_time.month,
        current_time.day,
        TARGETED_HOUR_BIRTHDAY_REMINDER[0],
        TARGETED_HOUR_BIRTHDAY_REMINDER[1],
    )
    logger_main.info(f"called")
    # Calculate delay before target time
    if current_time < target_time:
        wait_time: datetime = target_time - current_time
        logging.debug("wait time = %s", wait_time)
    else:
        next_day: datetime.datetime = current_time + datetime.timedelta(days=1)
        target_time = datetime.datetime(
            next_day.year,
            next_day.month,
            next_day.day,
            TARGETED_HOUR_BIRTHDAY_REMINDER[0],
            TARGETED_HOUR_BIRTHDAY_REMINDER[1],
        )
        wait_time: datetime.timedelta = target_time - current_time

    # waiting until target time
    logging.info("waiting %s seconds", wait_time.total_seconds())
    await asyncio.sleep(wait_time.total_seconds())

    asyncio.create_task(birthday_reminder.start())


@tasks.loop(hours=24)
async def birthday_reminder(
    sentence: str = DEFAULT_BIRTHDAY_WISHING_SENTENCE,
    channel_name: str = DEFAULT_GENERAL_CHANNEL,
):
    """Send a message on discord channel specified with sentence
    Args:
        sentence (str): start of sentence you want, somes string are added after
        channel_name (str): name of discord channel you want to send a message
    """
    logger_main.info("called")
    all_birthday: tuple[dict[str, str]] = await recovery_birthday(
    date=datetime.datetime.now(), logger=logger_main
    )
    if all_birthday is not None:
        logger_main.info(f"{len(all_birthday)} birthday(s) recovered")
        for birth in all_birthday:
            sentence += f"\n- {birth[DEFAULT_FIRSTNAME_KEY]} {birth[DEFAULT_NAME_KEY]}"
            if birth['formation'] == DEFAULT_CELEBRITE_KEY:
                wikipedia_link = f"https://fr.wikipedia.org/wiki/{birth['prenom']}_{birth['nom']}"
                sentence += f" ({wikipedia_link.replace('https://', 'Wiki Link: ')})"
        sentence += (
            "\nNous "
            + ("lui" if len(all_birthday) == 1 else "leur")
            + " souhaitons un joyeux anniversaire"
        )

        logger_main.debug(f"Sentence value: {sentence}")

        guild = bot.get_guild(IUT_SERV_ID)
        general_channel = utils.get(guild.channels, name=channel_name)
        await general_channel.send(sentence)



if __name__ == "__main__":
    disable_warnings(
        InsecureRequestWarning
    )  # Disable preventiv messages from requets module

    # Change local timezone
    os.environ["TZ"] = DEFAULT_TIMEZONE
    time.tzset()

    log_format = (
        "%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s : %(message)s"
    )
    log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format=log_format,
    )

    if not os.path.exists("Logs"):
        os.makedirs("Logs")

    # Retranscription des logs du script main
    logger_main = logging.getLogger(f"main.py")
    file_handler_main = logging.FileHandler("Logs/main_logs.txt")
    file_handler_main.setLevel(log_level)
    file_handler_main.setFormatter(logging.Formatter(log_format))
    logger_main.addHandler(file_handler_main)

    # Retranscription des logs du module discord
    logger_discord = logging.getLogger("discord")
    file_handler_discord = logging.FileHandler("Logs/discord_logs.txt")
    file_handler_discord.setLevel(log_level)
    file_handler_discord.setFormatter(logging.Formatter(log_format))
    logger_discord.addHandler(file_handler_discord)

    bot.run(TOKEN)
