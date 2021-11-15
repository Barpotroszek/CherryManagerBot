from os import system, getenv
import discord
from discord.ext import commands
from discord.ext.commands.errors import NoEntryPointError
from data.config import config
from dotenv import load_dotenv
load_dotenv()


bot = commands.Bot(
    config.commands_prefix,
    help_command=None
)

# funkcja testowa
async def is_admin(ctx):
    admin_role = discord.utils.get(
        ctx.author.guild.roles, name="Administratracja")
    return admin_role in ctx.author.roles


@bot.event
async def on_connect():
    print("Bot połączył się z Discordem.\nWczytywanie danych...")
    for cog in config.__cogs__:
        try:
            bot.load_extension(cog)
        except NoEntryPointError:
            print(f"Nie udało się załadować roszczerzenia {cog}")
    print("Dane wczytane")


@bot.event
async def on_ready():
    print("\nZalogowano jako:", bot.user)
    status = discord.Game(config.status)
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=status)
    print("----------------------------------")

@bot.command()

async def admin(ctx):
    """Mówi, czy dany użytkownik ma rolę \"Administrator\""""
    await ctx.send("Yes, you're admin")

@bot.command()
async def reload(ctx):
    """Reload all cogs"""
    system('cls')
    async with ctx.typing():
        embed = discord.Embed(
            title="Reloading cogs",
            color=0xb06a09,
            timestamp=ctx.message.created_at
        )

        for cog in config.__cogs__:
            try:
                bot.unload_extension(cog)
                bot.load_extension(cog)
                embed.add_field(
                    name=cog,
                    value="Reloaded",
                    inline=False
                )
            except Exception:
                embed.add_field(
                    name=cog,
                    value="Something gone wrong",
                    inline=False
                )
    
    msg = await ctx.send(embed=embed)
    await ctx.message.delete(delay=5)
    await msg.delete(delay=5)

@bot.command(
    usage="<text>",
    help="Powtarzanie podanego słowa"
    )
async def echo(ctx, echo_text):
    await ctx.send(echo_text)

'''@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title="on_command_error")
    embed.add_field(name=error, value=' ')
    await ctx.send(embed=embed)


@bot.event
async def on_error(event_error, *args, **kwargs):
    channel = bot.get_channel(894670655423934544)
    embed = discord.Embed(title = f"*{event_error}*", color=discord.Color.red())
    embed.add_field(name="args", value=args[1:] )
    embed.add_field(name="kwargs", value=str(kwargs))
    await channel.send("***Wleciał error***", embed=embed)
'''
if config.normal_work:
    bot.run(getenv("MAIN"))
else:
    bot.run(getenv("TEST"))