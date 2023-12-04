import requests
import logging
import asyncio
from datetime import date
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from constants import URL_BIRTHDAY_RECOVERY


async def recovery_birthday(
    date: date, logger: logging.Logger, url: str = URL_BIRTHDAY_RECOVERY
) -> list[dict[str, str, int]]:
    """Return list of dictionnarys {"nom" : name, "prenom" : firstname, "annee": year}
    Args:
        date (date): Date of birthdays
        logger (logging.Logger): Logger parametred for your logs
        url (str): URL for API request DEFAULT URL_BIRTHDAY_RECOVERY
    Returns:
        list[dict[str, str, int]]: list of all birthday recovered
    Raise:
        ValueError: If no birthday are found
    """
    logger.info("called")
    # URL Complétion with date
    #url += f"?d={date.day}&m={date.month}"
    url  = "https://anniversaire-iut.jrcandev.netlib.re/anniversaire_le_florient.php?d=16&m=11"
    try:
        # Data recovery
        response = requests.get(url, verify=False)
        if response.content == "null":  # No birthday
            logger.info("Not birthday found")
            raise ValueError
        else:
            logger.info(f"List of birthday found: {response.json()}")
            return response.json()

    except Exception as e:
        logger.critical(f"Error: service not accessed: {e}")


if __name__ == "__main__":
    disable_warnings(
        InsecureRequestWarning
    )  # Désactive des messages de prévention du module requests
    log_format = (
        "%(asctime)s | %(levelname)s | %(filename)s | %(funcName)s : %(message)s"
    )
    log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format=log_format,
    )

    logger_main: logging.Logger = logging.getLogger(f"utils.py")

    date1: date = date(1970, 11, 30)
    date2: date = date(1970, 11, 28)

    asyncio.run(recovery_birthday(date1, logger_main))
    asyncio.run(recovery_birthday(date2, logger_main))
