from datetime import datetime
from os import name, system
from discord.errors import NotFound
from discord.ext import commands
from discord.ext.commands import errors
import logging as log
from data.config.config import _json
from discord.message import Message


class ErrorsHandler(commands.Cog):
    def __init__(self, bot, logger: log) -> None:
        self.bot = bot
        self.ignored_errors = [errors.CommandNotFound]
        self.logger = logger
        self.logger.basicConfig(
            filename=f"cogs/ErrorsHandler/logs/{datetime.now().strftime('%d-%m-%Y %H-%M')}.log",
            filemode="a",
            level=log.ERROR,
            encoding="utf-8",
            datefmt="%H:%m %m/%d/%Y",
            format=
            """"%(name)s" [%(asctime)s] -> %(message)s"""
        )
        self.vars_file = "cogs/ErrorsHandler/vars.json"

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if type(error) in self.ignored_errors:
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.reply("Nie podano wymaganego argumentu: `{}`".format(error.param))

        elif isinstance(error, errors.BadArgument):
            await ctx.message.reply("Podano zły argument: `{}`".format(error.param))

        elif isinstance(error, errors.MessageNotFound):
            await ctx.message.reply("Wiadomość nie została znaleziona")
        
        elif isinstance(error, errors.MemberNotFound):
            await ctx.message.reply("Użytkownik nie został znaleziony")
        
        elif isinstance(error, errors.ChannelNotFound):
            await ctx.message.reply("Kanał nie został znaleziony")
        
        elif isinstance(error, errors.RoleNotFound):
            await ctx.message.reply("Rola nie została znaleziona")

        elif isinstance(error, errors.EmojiNotFound):
            await ctx.message.replu("Emoji nie zostało znalezione")

        elif isinstance(error, errors.MissingPermissions):
            await ctx.message.reply("Nie masz uprawnienia: `{}`".format(error.missing_perms))

        elif isinstance(error, errors.MissingRole):
            await ctx.message.reply("Nie masz wymaganej roli: `{}`".format(error.missing_role))

        elif isinstance(error, errors.MissingAnyRole):
            await ctx.message.reply("Nie masz żadnej z wymaganej ról")

        elif isinstance(error, errors.ExtensionNotLoaded):
            await ctx.message.reply(f"Dodatek `{error.name}` nie został załadowany")

        elif isinstance(error, errors.ExtensionFailed):
            await ctx.message.reply("Dodatek `{}` wyrzucił błąd, więcej info w logach".format(error.name))
            self.logger.error(error.original)
        
        elif isinstance(error, errors.DisabledCommand):
            await ctx.message.reply("Komenda `{}` została zablokowana".format(error.args))


        else:
            error = getattr(error, 'original', error)
            original = getattr(error, 'original', error)

            print([original])
            if hasattr(error, "params"):
                params = error.params
            else:
                params= ""
            _json(self.vars_file).write(dir(error))
            await ctx.message.reply("**Wystąpił błąd:** `{}`".format(error), mention_author=False)
            self.logger.getLogger(error.__class__.__name__).error(f"{error.args} {params}\n  Przyczyna: {error.__cause__}")


def setup(bot):
    bot.add_cog(ErrorsHandler(bot, log))
