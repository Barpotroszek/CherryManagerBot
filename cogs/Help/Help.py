import discord
from discord.ext import commands
from discord.errors import Forbidden
from data.config import config

"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py!
However, you must put "bot.remove_command('help')" in your bot, and the command must be in a cog for it to work.

Original concept by Jared Newsom (AKA Jared M.F.)
[Deleted] https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b
Rewritten and optimized by github.com/nonchris
https://gist.github.com/nonchris/1c7060a14a9d94e7929aa2ef14c41bc2

You need to set three variables to make that cog run.
Have a look at line 51 to 57
"""


async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(commands.Cog):
    """Sends this help message"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage=f"<command>")
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *input):
        """Shows all modules of that bot"""

        def give_usage(command):
            return command.usage if command.usage != None else ""

        # !SET THOSE VARIABLES TO MAKE THE COG FUNCTIONAL!
        prefix = config.commands_prefix # ENTER YOUR PREFIX - loaded from config, as string or how ever you want!
        version =  config.version # enter version of your code

        # setting owner name - if you don't wanna be mentioned remove line 49-60 and adjust help text (line 88)
        owner = config.owners_id	# ENTER YOU DISCORD-ID
        owner_name = "Barpotroszek#1584"	# ENTER YOUR USERNAME#1234


        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if not input:
            # checks if owner is on this server - used to 'tag' owner
            try:
                owner = await self.bot.fetch_user(owner).name
            except Exception as e:
                print("Got error in help:\n\t", e.args, e)
                owner = owner_name

            # starting to build embed
            emb = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                                description=f'Use `{prefix}help <command>` to gain more information about that command'
                                            f':smiley:\n')

            # iterating trough cogs, gathering descriptions
            for cog in self.bot.cogs:
                cogs_desc = ''
                for command in self.bot.get_cog(cog).get_commands():
                    cogs_desc += f'`{prefix}{command.name} {give_usage(command)}` -> {command.help}\n'
                cogs_desc = self.bot.get_cog(cog).description if cogs_desc == "" else cogs_desc
                emb.add_field(name=cog, value=cogs_desc, inline=False)

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'`{prefix}{command.name} {give_usage(command)}` -> {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Not belonging to any module',
                              value=commands_desc, inline=False)

            # setting information about author
            emb.add_field(name="About", value=f"The Bots is developed by Barpotroszek#1584, based on discord.py.\n\
                                    This version of it is maintained by {owner}\n\
                                    Please visit https://github.com/nonchris/discord-fury to submit ideas or bugs.")
            emb.set_footer(text=f"Bot is running {version}")

        # block called when one cog-name is given
        # trying to find matching cog and/or it's commands
        elif len(input) >= 1:
            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'Cog *`{cog}`* - Commands', description=self.bot.cogs[cog].__doc__,
                                        color=discord.Color.green())

                    # getting commands from cog
                    for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            emb.add_field(name=f"`{prefix}{command.name}`", value=f"  {command.help}", inline=False)
                    # found cog - breaking loop
                    break

                else:
                    emb=None
                    # getting commands from cogs
                    for command in self.bot.get_cog(cog).get_commands():
                        # if command.name equals input
                        if command.name == input[0].lower():
                            if type(command) == discord.ext.commands.core.Group:
                                emb = discord.Embed(title=f"`{prefix}{input[0]}` - {cog} Command", color=discord.Color.green())

                                emb.add_field(name=f"`{prefix}{command}`", value=command.help, inline=False)
                                values = []
                                for option in command.walk_commands():
                                    values.append(f"`{prefix}{command} {option.name} {give_usage(option)}` -> {option.help}")
                                emb.add_field(name="Options:", value="\n".join(values))
                            # found function - breaking loop
                            break
                    if emb != None:
                        break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="What's that?!",
                                    description=f"I've never heard about commnand called `{input[0]}` before :scream:",
                                    color=discord.Color.orange())

        '''
        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="That's too much.",
                                description="Please request only one module at once :sweat_smile:",
                                color=discord.Color.orange())

        else:
            emb = discord.Embed(title="It's a magical place.",
                                description="I don't know how you got here. But I didn't see this coming at all.\n"
                                            "Would you please be so kind to report that issue to me on github?\n"
                                            "https://github.com/nonchris/discord-fury/issues\n"
                                            "Thank you! ~Chris",
                                color=discord.Color.red())
                                '''

        # sending reply embed using our own function defined above
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Help(bot))
