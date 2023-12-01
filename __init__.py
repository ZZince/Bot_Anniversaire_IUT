import datetime
import logging
import asyncio
import os
import time
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from discord import Intents, utils, Bot
from discord.ext import tasks
from modules.utils import recovery_birthday
from modules.constants import (
    TARGETED_HOUR_BIRTHDAY_REMINDER,
    DEFAULT_BIRTHDAY_WISHING_SENTENCE,
    DEFAULT_FIRSTNAME_KEY,
    DEFAULT_NAME_KEY,
    IUT_SERV_ID,
    DEFAULT_GENERAL_CHANNEL,
    DEFAULT_TIMEZONE,
)
from modules._token import TOKEN
