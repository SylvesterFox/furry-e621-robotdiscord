import logging
import asyncio
import discord
import traceback
import sys

from discord.ext import commands
from discord.ext.commands import errors
from utils.bot import token
from utils.uwu import E621connect
from datetime import datetime
from utils.database import create_table, get_all, update_post_id


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cfg = token()
        self.e621_api = E621connect(username=self.cfg[1], token=self.cfg[0])
        self.logger = logging.getLogger('cogs.Events')

    async def task_parser(self):
        avatar = self.bot.user.avatar_url
        while True:
            if not get_all():
                pass

            async def send_post(item, data):
                    embed = discord.Embed(title=f"New file matches your tags \"{item['tag']}\"",
                                          description=f"Url: [Page](https://e621.net/post/show/{data['posts'][0]['id']}),"
                                                      f"[file]({data['posts'][0]['file']['url']})",
                                          color=discord.Colour.random()
                                          )
                    embed.set_image(url=data['posts'][0]['file']['url'])
                    embed.set_author(name="DvDFurryBot", icon_url=f"{avatar}")
                    _datetime = datetime.now()
                    embed.set_footer(text=f'date post: {_datetime.strftime("%d/%m/%y %H:%M")}',
                                     icon_url=f"{avatar}")

                    channel = self.bot.get_channel(item['channel_id'])
                    await channel.send(embed=embed)
                    self.logger.info('sending post... ')
            
            async def get_response_post():
                data = await self.e621_api.get_request(tag=item['tag'], activate_tag=item['activate'])
                try:
                    if data['posts'][0]['id'] == item['id_tag']:
                        pass
                    else:
                        update_post_id(id=item['id'], post_id=data['posts'][0]['id'])
                        return data
                except Exception as e:
                    pass


            for item in get_all():
                post_response = await get_response_post()
                if post_response:
                    await send_post(item=item, data=post_response)

                    
            await asyncio.sleep(120)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Starting bot")
        print("Bot, is ready")
        create_table()
        await self.bot.loop.create_task(self.task_parser())

    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            await ctx.send_help(ctx.command)

        if isinstance(err, errors.CommandNotFound):
            pass

        if isinstance(err, errors.CommandInvokeError):
            original = err.original
            await ctx.send(f"There was an error processing the command ＞﹏＜")
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}', file=sys.stderr)

        if isinstance(err, commands.DisabledCommand):
            await ctx.send('Sorry. This command is disabled and cannot be used.')

        if isinstance(err, commands.ArgumentParsingError):
            await ctx.send(err)


def setup(bot):
    bot.add_cog(Events(bot))
