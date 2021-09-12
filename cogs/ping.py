from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='ping',
        description='Check ping bot.'
    )
    async def _ping(self, ctx):
        msg = await ctx.send('Pong!')
        await msg.edit(f'> My ping: `{round(self.bot.latency * 1000)}`')


def setup(bot):
    bot.add_cog(Ping(bot))
