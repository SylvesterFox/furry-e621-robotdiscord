import logging
import asyncio
import discord
import traceback
import sys
import math

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
                        self.logger.info(f"Send post, id post:{data['posts'][0]['id']}")
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

        if isinstance(err, errors.BotMissingPermissions):
            await ctx.send("You are not authorized to use this command.")

    @commands.group(
        name="Help",
        aliases=['help', 'h', 'commands'],
        description="Help command"
    )
    async def _help(self, ctx):
        if ctx.invoked_subcommand is None:
            cog = 1
            helpEmbed = discord.Embed(
                title="Help command!",
                color=discord.Colour.blurple()
            )
            helpEmbed.set_thumbnail(url=ctx.author.avatar_url)
            helpEmbed.set_author(icon_url=self.bot.user.avatar_url, name='Prefix bot: `d!`')

            cogs = [c for c in self.bot.cogs.keys()]
            cogs.remove('Events')

            totalPages = math.ceil(len(cogs) / 4)

            cog = int(cog)
            if cog > totalPages or cog < 1:
                await ctx.send(f"Invalid page number: `{cog}`\nAlternatively, simpy run `help` to see the first help page")
                return

            neededCogs = []
            for i in range(4):
                x = i + (int(cog) - 1) * 4
                try:
                    neededCogs.append(cogs[x])
                except IndexError:
                    pass

            for cog in neededCogs:
                commandList = ""
                for command in self.bot.get_cog(cog).walk_commands():
                    if command.hidden:
                        continue
                    elif command.parent != None:
                        continue

                    commandList += f"`{command.name}` - **{command.description}**\n"
                commandList += "\n"

                helpEmbed.add_field(name=cog, value=commandList, inline=False)

            await ctx.send(embed=helpEmbed)

    @_help.command(
        name='command'
    )
    async def _command(self, ctx, command: str):
        await ctx.send_help(command)

    @_help.command(
        name="page"
    )
    async def _page(self, ctx, cog: int):
        helpEmbed = discord.Embed(
            title="Help command!",
            color=discord.Colour.blurple()
        )
        helpEmbed.set_thumbnail(url=ctx.author.avatar_url)
        helpEmbed.set_author(icon_url=self.bot.user.avatar_url, name='Prefix bot: `d!`')

        cogs = [c for c in self.bot.cogs.keys()]
        cogs.remove('Events')

        totalPages = math.ceil(len(cogs) / 4)

        cog = int(cog)
        if cog > totalPages or cog < 1:
            await ctx.send(f"Invalid page number: `{cog}`\nAlternatively, simpy run `help` to see the first help page")
            return

        neededCogs = []
        for i in range(4):
            x = i + (int(cog) - 1) * 4
            try:
                neededCogs.append(cogs[x])
            except IndexError:
                pass

        for cog in neededCogs:
            commandList = ""
            for command in self.bot.get_cog(cog).walk_commands():
                if command.hidden:
                    continue
                elif command.parent != None:
                    continue

                commandList += f"`{command.name}` - **{command.description}**\n"
            commandList += "\n"

            helpEmbed.add_field(name=cog, value=commandList, inline=False)

        await ctx.send(embed=helpEmbed)


def setup(bot):
    bot.add_cog(Events(bot))
