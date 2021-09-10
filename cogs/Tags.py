import discord

from discord.ext import commands
from utils.bot import token
from utils.database import insert_data, get_tags_server, delete_tag, update_activate, get_activate


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cfg = token()

    @commands.command(aliases=['addtag'])
    @commands.is_nsfw()
    @commands.is_owner()
    async def _AddTag(self, ctx, channel: discord.TextChannel, tag: str):
        if channel.nsfw:
            insert_data(guild_id=ctx.guild.id, channel_id=channel.id, tag=tag, activate=True, user=ctx.author.id)

            embed = discord.Embed(
                title='Add tag',
                color=discord.Colour.green()
            )
            embed.add_field(name='Channel', value=f'<#{channel.id}>', inline=False)
            embed.add_field(name='Tags', value=tag, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Channel not nsfw')

    @commands.command(aliases=['viewtags', 'tags'])
    @commands.is_nsfw()
    @commands.is_owner()
    async def _ViewTags(self, ctx):
        data = get_tags_server(guild_id=ctx.guild.id, user_id=ctx.author.id)
        embed = discord.Embed(title='Tag list', color=discord.Colour.red())
        for item in data:
            embed.add_field(name=f'{item["tag"]}', value=f'__**id:**__ `{item["id"]}` __**channel:**__ <#{item["channel_id"]}> __**activate:**__ `{item["activate"]}`', inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['tagdelete', 'rmtag', 'tagdel'])
    @commands.is_nsfw()
    @commands.is_owner()
    async def _deleteTag(self, ctx, id: int):
        delete_tag(user_id=ctx.author.id, id=id)
        await ctx.send(f"Delete tag, id: {id}")

    @commands.command(aliases=['pause', 'stop', 'activatetag'])
    async def _activateTagcontrol(self, ctx, id: int):
        data = get_activate(id=id)
        if data[0]["activate"]:
            update_activate(id=id, switch=False)
            embed = discord.Embed(color=discord.Colour.dark_orange())
            embed.set_author(icon_url=self.bot.user.avatar_url, name='Pause posting tag')
            embed.add_field(name=f'{data[0]["tag"]}', value=f'Tags id: `{data[0]["id"]}` **__deactivate__**, channel: <#{data[0]["channel_id"]}>')
            await ctx.send(embed=embed)
        else:
            update_activate(id=id, switch=True)
            embed = discord.Embed(color=discord.Colour.dark_orange())
            embed.set_author(icon_url=self.bot.user.avatar_url, name='Pause posting tag')
            embed.add_field(name=f'{data[0]["tag"]}', value=f'Tags id: `{data[0]["id"]}` **__activate__**, channel: <#{data[0]["channel_id"]}>')
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Tags(bot))