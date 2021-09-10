import os
import logging

from utils.bot import Bot
from utils.bot import token



start_app = Bot(
    command_prefix="d!",
    prefix="d!",
    command_attrs=dict(hidden=True),
)

tokens = token()

start_app.remove_command("help")

logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)

fh = logging.FileHandler("bot.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        logger.info(f'[Extension] install - {name}')
        start_app.load_extension(f"cogs.{name}")


start_app.run(tokens[2])
