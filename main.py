import datetime
import logging
import asyncio
import os
import time
from typing import Callable
from platform import system
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from discord import Intents, utils, Bot
from discord.ext import tasks
from utils import recovery_birthday
from constants import (
    TARGETED_HOUR_BIRTHDAY_REMINDER,
    TARGETED_HOUR_RESET_TOPIC,
    DEFAULT_FIRSTNAME_KEY,
    DEFAULT_NAME_KEY,
    DEFAULT_GENERAL_CHANNEL,
    DEFAULT_TIMEZONE,
    DEFAULT_CELEBRITE_KEY,
    DEFAULT_TOPIC,
)


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

    await wait_for_auto_start_function(
        birthday_reminder, *TARGETED_HOUR_BIRTHDAY_REMINDER
    )
    await wait_for_auto_start_function(reset_topic, *TARGETED_HOUR_RESET_TOPIC)


async def wait_for_auto_start_function(
    function: Callable,
    hour: int,
    minute: int,
):
    """Lance la fonction demandé à l'heure indiquée

    Args:
        function (function): Fonction à lancer
        hour (int): Heure à laquelle lancer la fonction
        minute (int): Minute à laquelle lancer la fonction
    """

    current_time: datetime.datetime = datetime.datetime.now()
    target_time: datetime.datetime = datetime.datetime(
        current_time.year,
        current_time.month,
        current_time.day,
        hour=hour,
        minute=minute,
    )
    logger_main.info(f"called")
    logger_main.debug(f"target_time = {target_time}")
    logger_main.debug(f"current_time = {current_time}")
    logger_main.debug(f"Is current_time < target time: {current_time < target_time}")
    # Calculate delay before target time
    if current_time < target_time:
        wait_time: datetime = target_time - current_time
        logging.debug("wait time = %s", wait_time)
    else:
        next_day: datetime.datetime = current_time + datetime.timedelta(days=1)
        wait_time: datetime.timedelta = next_day - current_time
        logging.debug("wait time = %s", wait_time)

    # waiting until target time
    logging.info("waiting %s seconds", wait_time.total_seconds())
    logger_main.debug(
        f"Function is coroutine ? {asyncio.iscoroutinefunction(function)}"
    )
    await asyncio.sleep(wait_time.total_seconds())
    asyncio.create_task(function())


@tasks.loop(hours=24)
async def birthday_reminder(
    channel_name: str = DEFAULT_GENERAL_CHANNEL,
    guild_id: int = int(os.getenv("IUT_SERV_ID")),
):
    """Send a message on discord channel specified with sentence
    Args:
        channel_name (str): name of discord channel you want to send a message
    """
    logger_main.info("called")
    all_birthday: tuple[dict[str, str]] = await recovery_birthday(
        date=datetime.datetime.now(), logger=logger_main
    )
    if all_birthday is not None:
        sentence = "Aujourd'hui nous souhaitons l'anniversaire de: "
        logger_main.info(f"{len(all_birthday)} birthday(s) recovered")
        for birth in all_birthday:
            sentence += f"\n- {birth[DEFAULT_FIRSTNAME_KEY]} {birth[DEFAULT_NAME_KEY]}"
            if birth["formation"] == DEFAULT_CELEBRITE_KEY:
                wikipedia_link = (
                    f"<https://fr.wikipedia.org/wiki/{birth['prenom']}_{birth['nom']}>"
                )
                sentence += f" ({wikipedia_link})"
        sentence += (
            "\nNous "
            + ("lui" if len(all_birthday) == 1 else "leur")
            + " souhaitons un joyeux anniversaire"
        )

        logger_main.debug(f"Sentence value: {sentence}")

        new_topic = DEFAULT_TOPIC + " Aujourd'hui: "
        for birth in all_birthday:
            if birth["formation"] == DEFAULT_CELEBRITE_KEY:
                continue
            else:
                new_topic += (
                    f"{birth[DEFAULT_FIRSTNAME_KEY]} {birth[DEFAULT_NAME_KEY]}, "
                )
        new_topic = new_topic[:-2]

        logger_main.debug(f"New topic value: {new_topic}")

        logging.debug(f"Valeur de os.getenv('IUT_SERV_ID'): {os.getenv('IUT_SERV_ID')}")
        guild = bot.get_guild(guild_id)
        general_channel = utils.get(guild.channels, name=channel_name)
        await general_channel.send(sentence)
        await general_channel.edit(topic=new_topic)


@tasks.loop(hours=24)
async def reset_topic(
    channel_name: str = DEFAULT_GENERAL_CHANNEL,
    guild_id: int = int(os.getenv("IUT_SERV_ID")),
):
    """Reset the topic of the channel specified
    Args:
        channel_name (str): name of discord channel you want to reset the topic
        guild_id (int): id of the guild where the channel is
    """
    logger_main.info("called")
    guild = bot.get_guild(guild_id)
    general_channel = utils.get(guild.channels, name=channel_name)
    await general_channel.edit(topic=DEFAULT_TOPIC)


if __name__ == "__main__":
    disable_warnings(
        InsecureRequestWarning
    )  # Disable preventiv messages from requets module

    # Change local timezone
    if system() == "Linux":
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

    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Retranscription des logs du script main
    logger_main = logging.getLogger(f"main.py")
    file_handler_main = logging.FileHandler("logs/main_logs.txt")
    file_handler_main.setLevel(log_level)
    file_handler_main.setFormatter(logging.Formatter(log_format))
    logger_main.addHandler(file_handler_main)

    logger_main.info("Platform: %s", system())

    bot.run(os.getenv("TOKEN"))
