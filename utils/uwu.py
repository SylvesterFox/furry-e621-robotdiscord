import aiohttp
import logging


class E621connect:
    def __init__(self, username, token):
        self.user = username
        self.token = token
        self.logger = logging.getLogger('utils.uwu')

    async def get_request(self, tag, activate_tag):
        if activate_tag:
            Head = {"User-Agent": "DvDFurryBotDiscord/1.0 (SylvesterFox)"}
            URL = f"https://e621.net/posts.json?tags={tag}"
            URLgrab = f"{URL}&limit=1"

            if self.user != None and self.token:
                auth = aiohttp.BasicAuth(login=self.user, password=self.token)
                async with aiohttp.ClientSession(auth=auth, headers=Head) as session:
                    try:
                        async with session.get(URLgrab) as response:
                            if response.status == 200:
                                return await response.json()
                    except aiohttp.ClientConnectionError as e:
                        return self.logger.error(f"Unable to connect {e}")

