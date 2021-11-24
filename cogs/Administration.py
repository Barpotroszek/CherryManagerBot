import discord
import subprocess as sub
from config import config
from config.config import cache
from discord.ext import commands
from config.core import GuildParams
from discord.ext.commands import converter
from discord.permissions import Permissions

class Administration(commands.Cog):
    """Dane statystyczne, itp."""
    def __init__(self, bot):
        self.bot = bot
        cache['DMessages'] = []


    @commands.command(name="stats")
    async def stats(self, ctx):
        """Wyświetlanie statystyk tego bota"""
        bot = self.bot
        embed = discord.Embed(
            title = f"{bot.user.name}'s stats",
            colour = discord.Colour(0x6712a3),
            description = "Statystyki bota!",
        )
        embed.add_field(name="Bot version:", value=config.version, inline=True)
        embed.add_field(name="Total guilds amount:", value=len(bot.guilds), inline=True)
        roles = [str(f'{a.mention}') for a in ctx.guild.roles]
        sth = ', '.join(roles)
        
        embed.add_field(
            name="All roles:",
            value=sth, 
            inline=False
            )       
        
        embed.add_field(
            name="Modules: ",
            value="**->**"+"\n **-> **".join(self.bot.cogs)+"",
            inline=True
        )

        await ctx.send(embed=embed)
    
    @commands.command()
    async def beginning(self, ctx):
        """Set default settings"""
        async with ctx.typing():
            perm = Permissions()

            guild = ctx.guild
            everyone = await commands.converter.RoleConverter().convert(ctx, "@everyone")
            try:
                channel = await commands.converter.TextChannelConverter().convert(ctx, "witamy")
                await channel.edit(
                    name="bałagan",
                    position=0
                )
                perm.update(read_messages=False, send_messages=False, connect=False, speak=False )
                await everyone.edit(permissions=perm)
                await channel.set_permissions(target=everyone, read_messages=True, send_messages=True)
            except Exception as e:
                await ctx.send(e)
                pass
            
            created_channels={}
            # poszukiwanie/tworzenie kanałów wymienionych powyżej
            for channel in config.default_channels:
                if channel not in [ch.name for ch in ctx.guild.text_channels]:
                    await ctx.send(f"Ni ma kanału `{channel}`, bida w kraju")
                    channel = await guild.create_text_channel(channel)
                else:
                    await ctx.send(f"Yo yo, jest kanał `{channel}`")
                    channel = await converter.TextChannelConverter().convert(ctx, channel)
                await channel.set_permissions(target=everyone, read_messages=True, send_messages=False)
                created_channels[channel.name] = channel

            # poszukiwanie roli spectatora
            r_spectator = None
            for role in ctx.guild.roles:
                if "👀spectator" == role.name:
                    r_spectator = role
                    perm.update(read_messages=True, send_messages=False, connect=True, speak=True, stream=True)
                    await r_spectator.edit(permissions=perm,colour = discord.Color(0xffffff))
                    await ctx.send("Oczka znalezione c:")
                    break
            else:
                await ctx.send("No kurde, oczek też ni ma")
                r_spectator = await guild.create_role(name="👀spectator")
                perm.update(read_messages=True, send_messages=False, connect=True, speak=True, stream=True)
                await r_spectator.edit(permissions=perm,colour = discord.Color(0xffffff))
                await ctx.send("Dodano role *👀spectator*")


            GuildParams(guild.id).add_new(created_channels, r_spectator.id)
        text = ",".join([f"`{ch}`" for ch in config.default_channels])
        await ctx.send(f"Made first setup\n **Pamiętaj, by zmienić uprawnienia dla kanałów: {text} !!!!!**")    

    @commands.command(name="git", usage="<option>", help="Sterowanie gitem")
    async def git(self, ctx, *args):    
        if ctx.author.id not in config.owners_id:
            await ctx.reply("Tylko właściciel bota może użyć tej komendy")
            return
        if len(args)==0:
            cmd = ['git', "status"]
        else:
            cmd = ['git']+[a for a in args]
        proc = sub.run(" ".join(cmd), shell=True, text=True, capture_output=True)
        await ctx.send(f"```sh\n{proc.stdout}```")


'''
    @commands.command(usage="")
    async def guard_role(self, ctx, role: discord.Role, color):
        """nie"""
        pass
'''

def setup(bot):
    bot.add_cog(Administration(bot))