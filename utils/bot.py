import logging
import json
import os

from discord.ext.commands import AutoShardedBot


def settings_app():
    with open("appsettings.json", "r") as setting:
        data = json.load(setting)
        return data


def token():
    tokens = settings_app()
    if tokens['heroku_mod']:
        e621user = os.environ['e621user']
        e621token = os.environ['e621token']
        token_bot = os.environ['token_bot']
        return [e621token, e621user, token_bot]
    else:
        e621user = tokens['E621User']
        e621token = tokens['E621Token']
        token_bot = tokens['Token']
        return [e621token, e621user, token_bot]


class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('bot')


