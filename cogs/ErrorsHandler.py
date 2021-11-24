import sys
import discord
import difflib
import logging as log
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import errors
from config.core import _json, LOGS_DIR_PATH
from config.config import cache


class ErrorsHandler(commands.Cog):
    def __init__(self, bot, logger: log) -> None:
        self.bot = bot
        self.ignored_errors = []
        self.logger = logger
        self.logger.basicConfig(
            filename=f"{LOGS_DIR_PATH}/{datetime.now().strftime('%d-%m-%Y %H-%M')}.log",
            filemode="a",
            level=log.ERROR,
            # encoding="utf-8",
            datefmt="%H:%m %m/%d/%Y",
            format=
            """"\n\n\n%(name)s" [%(asctime)s] -> %(message)s"""
        )
        self.commands = [cmd.name for cmd in self.bot.walk_commands()]
        self.vars_file = "vars.json"

    async def reply(self, msg):
        '''Wysyłanie odpowiedzi na wysłaną komendę'''
        await self.ctx.message.reply(msg, mention_author = False)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        '''Wyłapuje wszystkie errory wykonane przez wywołane komendy'''
        if type(error) in self.ignored_errors:
            return
        
        self.ctx = ctx
        if isinstance(error, errors.CommandNotFound):
            '''Dopasowywanie komend'''
            cmd = ctx.message.content[1:].split(" ")[0]
            cache["not_found_error"] = cmd
            print("Content: ", cmd)
            print(error)
            matches = difflib.get_close_matches(cmd, self.commands)
            if matches != []:
                await ctx.send("Chodziło ci o: `{}`?".format(", ".join(matches)))

        elif isinstance(error, commands.MissingRequiredArgument):
            await self.reply("Nie podano wymaganego argumentu: `{}`".format(error.param))

        elif isinstance(error, errors.BadArgument):
            await self.reply("Podano zły argument: `{}`".format(error.param))

        elif isinstance(error, errors.MessageNotFound):
            await self.reply("Wiadomość nie została znaleziona")
        
        elif isinstance(error, errors.MemberNotFound):
            await self.reply("Użytkownik nie został znaleziony")
        
        elif isinstance(error, errors.ChannelNotFound):
            await self.reply("Kanał nie został znaleziony")
        
        elif isinstance(error, errors.RoleNotFound):
            await self.reply("Rola nie została znaleziona")

        elif isinstance(error, errors.EmojiNotFound):
            await ctx.message.replu("Emoji nie zostało znalezione")

        elif isinstance(error, errors.MissingPermissions):
            await self.reply("Nie masz uprawnienia: `{}`".format(error.missing_perms))

        elif isinstance(error, errors.MissingRole):
            await self.reply("Nie masz wymaganej roli: `{}`".format(error.missing_role))

        elif isinstance(error, errors.MissingAnyRole):
            await self.reply("Nie masz żadnej z wymaganej ról")

        elif isinstance(error, errors.ExtensionNotLoaded):
            await self.reply(f"Dodatek `{error.name}` nie został załadowany")

        elif isinstance(error, errors.ExtensionFailed):
            await self.reply("Dodatek `{}` wyrzucił błąd, więcej info w logach".format(error.name))
            self.logger.error(error.original)
        
        elif isinstance(error, errors.DisabledCommand):
            await self.reply("Komenda `{}` została zablokowana".format(error.args))

        else:
            error = getattr(error, 'original', error)

            #print([original])
            if hasattr(error, "params"):
                params = error.params
            else:
                params= ""
            _json(self.vars_file).write(dir(error))
            await self.reply("**Wystąpił błąd:** `{}: {}`".format(error.__class__.__name__, error))
            self.logger.getLogger(error.__class__.__name__).exception(f"{error.args} {params}", exc_info=error)
    
    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        owner = commands.Bot.get_user(config.owners_id)
        emb = discord.Embed(title=event)
        emb.add_field("Args:", value=f"`{args}`")
        emb.add_field("Kwargs:", value=f"`{kwargs}`")
        emb.add_field("Traceback", sys)
        emb.set_footer("Oczywiście więcej informacji znajdziesz w logach 😉")
        await owner.send("Cześć.\n  Głupia sytuacja, ale no wywaliło mi błąd:", embed=emb)
        self.logger.getLogger(event).exception(f"{args} {kwargs}", exc_info=sys.exc_info())


def setup(bot):
    bot.add_cog(ErrorsHandler(bot, log))
