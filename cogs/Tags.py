import discord
import logging

from discord.ext import commands
from utils.bot import token
from utils.database import get_tag_data, insert_data, get_tags_server, delete_tag, update_activate
from utils.database import all_user_activate, all_remove
from discord_components import Button, ButtonStyle


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cfg = token()
        self.log = logging.getLogger('cogs.Tag')

    @commands.command(
        name='addtag',
        description='Add tag.'
    )
    @commands.is_nsfw()
    @commands.is_owner()
    async def _add_tag(self, ctx, channel: discord.TextChannel, tag: str, sub=None, sub_tag=None):
        if channel.nsfw:
            if sub is None:
                insert_data(guild_id=ctx.guild.id, channel_id=channel.id, tag=tag, activate=True, user=ctx.author.id)
                embed = discord.Embed(
                    title='Add tag',
                    color=discord.Colour.green()
                )
                embed.add_field(name='Channel', value=f'<#{channel.id}>', inline=False)
                embed.add_field(name='Tags', value=tag, inline=False)
                await ctx.send(embed=embed, delete_after=30)
            elif sub:
                insert_data(guild_id=ctx.guild.id, channel_id=channel.id, tag=f"{tag}+{sub}{sub_tag}",
                            activate=True,
                            user=ctx.author.id)
                embed = discord.Embed(
                    title='Add tag',
                    color=discord.Colour.green()
                )
                embed.add_field(name='Channel', value=f'<#{channel.id}>', inline=False)
                embed.add_field(name='Tags', value=f"{tag}+{sub}{sub_tag}", inline=False)
                await ctx.send(embed=embed, delete_after=30)

        else:
            await ctx.send('Channel not nsfw', delete_after=30)

    @commands.command(
        name='viewtags',
        aliases=['tags'],
        description='List tags'
    )
    @commands.is_nsfw()
    @commands.has_permissions()
    async def _view_tags(self, ctx):
        async def callback(interaction):
            if interaction.user.id == ctx.author.id:
                await interaction.send(content="Closed!")
                await msg.delete()

        data = get_tags_server(guild_id=ctx.guild.id, user_id=ctx.author.id)
        if not data:
            return await ctx.send("not found tag...")
        component = [
            self.bot.components_manager.add_callback(
                Button(label='Close', style=ButtonStyle.red, emoji='❌', custom_id="1"), callback
            ),
        ]
        embed = discord.Embed(title='Tag list', color=discord.Colour.red())
        for item in data:
            embed.add_field(name=f'{item["tag"]}',
                            value=f'__**id:**__ `{item["id"]}` __**channel:**__ <#{item["channel_id"]}> __**activate:**__ `{item["activate"]}`',
                            inline=False)

        msg = await ctx.send(embed=embed, components=component)

    @commands.command(
        name='tagdelete',
        aliases=['rmtag', 'tagdel'],
        description='Remove tags'
    )
    @commands.is_nsfw()
    @commands.has_permissions()
    async def _delete_tag(self, ctx, id: int):
        data = get_tag_data(id=id)
        delete_tag(user_id=ctx.author.id, id=id)
        embed = discord.Embed(
                            color=discord.Colour.red(),
                            description=f"Delete tag: `{data[0]['tag']}`\nId: `{id}`"
                              )
        embed.set_author(icon_url=self.bot.user.avatar_url, name='Delete Tag!')
        await ctx.send(embed=embed, delete_after=30)

    @commands.command(
        name='pause',
        aliases=['stop', 'activatetag'],
        description='Stop posting tag.'
    )
    @commands.is_nsfw()
    @commands.has_permissions()
    async def _activate_tag_control(self, ctx, id_tag: int):
        data = get_tag_data(id=id_tag)
        if data[0]["activate"]:
            update_activate(id=id, switch=False)
            embed = discord.Embed(color=discord.Colour.dark_orange())
            embed.set_author(icon_url=self.bot.user.avatar_url, name='Pause posting tag')
            embed.add_field(name=f'{data[0]["tag"]}',
                            value=f'Tags id: `{data[0]["id"]}` **__deactivate__**, channel: <#{data[0]["channel_id"]}>')
            await ctx.send(embed=embed, delete_after=30)
        else:
            update_activate(id=id, switch=True)
            embed = discord.Embed(color=discord.Colour.dark_orange())
            embed.set_author(icon_url=self.bot.user.avatar_url, name='Pause posting tag')
            embed.add_field(name=f'{data[0]["tag"]}',
                            value=f'Tags id: `{data[0]["id"]}` **__activate__**, channel: <#{data[0]["channel_id"]}>')
            await ctx.send(embed=embed, delete_after=30)

    @commands.command(
        name='allactivate',
        description='All control activate posting'
    )
    @commands.is_nsfw()
    @commands.has_permissions()
    async def _all_activate_tag(self, ctx, switch: int):
        if switch == 0:
            all_user_activate(user_id=ctx.author.id, switch=False)
            await ctx.send('> Disabled all tags done!', delete_after=30)
        if switch == 1:
            all_user_activate(user_id=ctx.author.id, switch=True)
            await ctx.send('> Activate all tags done!', delete_after=30)

    @commands.command(
        name='removeall',
        description='Remove all tags'
    )
    @commands.is_nsfw()
    @commands.has_permissions()
    async def _remove_all_tag(self, ctx):
        async def callback(interaction):
            if interaction.user.id == ctx.author.id:
                if interaction.custom_id == "true":
                    await interaction.send(content="Tags all deletes...")
                    await msg.delete()
                    all_remove(user_id=ctx.author.id)
                elif interaction.custom_id == "false":
                    await interaction.send(content="Oke..")

        component = [
            self.bot.components_manager.add_callback(
                Button(label="Yes!", style=ButtonStyle.green, custom_id="true"), callback
            ),
            self.bot.components_manager.add_callback(
                Button(label="No", style=ButtonStyle.red, custom_id="false"), callback
            )
        ]
        embed = discord.Embed(
                            color=discord.Colour.red(),
                            description="Do you really want to remove all tags?"
                              )
        embed.set_author(name="WARING!")
        msg = await ctx.send(embed=embed, components=component)


def setup(bot):
    bot.add_cog(Tags(bot))
