import os
from os.path import join
from discord.file import File
from config import config
from discord.ext import commands
from discord.embeds import Embed
from asyncio.exceptions import TimeoutError

class FileSending(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dirs_to_check = [ "data", "cogs"] # dirs, where program will look for files
        
    @commands.command(name="send", usage="<file_index>", help="Zwraca podany plik")
    async def send_file(self, ctx, number: int = None):
        '''Zwraca plik, którego index został podany. Jeśli nie podano indeksu, zwraca ich liste i czeka na liczbę'''
        if ctx.author.id not in config.owners_id:
            await ctx.reply("Tylko właściciel bota może użyć tej komendy")
            return

        paths_list, counter = [], 0
        embed = Embed(title="Wysyłanie pliku")
        for dir in self.dirs_to_check:
            for (path, dirs, files) in os.walk(dir):
                if path.startswith("..") or "__pycache__" in path:
                    # await ctx.send(f"Ignored path: {path}")
                    continue
                desc = ""
                print(files)
                for file in files:
                        if not file.endswith(".py"):
                            desc += f"{counter}. `{file}`\n"
                            #await ctx.send(desc)
                            paths_list.append((join(path, file), file))
                            counter += 1
                if desc != "":
                    embed.add_field(name=f"Ścieżka: {path}", value=desc, inline=False)
        del(desc, counter)
        def return_path(msg):
            return ctx.author == msg.author

        if number is None:
            embed.set_footer(text="Podaj numer wybranego pliku")
            await ctx.send(embed=embed)

            try:
                msg = await self.bot.wait_for("message", timeout=10.0, check=return_path)
                number = int(msg.content)
            except TimeoutError:
                await ctx.channel.send("*Timeout*")
                return

        del(embed)
        file_path, filename = paths_list[number]
        print(file_path, filename)
        await ctx.reply(file=File(file_path, filename), mention_author=True)

def setup(bot):
    bot.add_cog(FileSending(bot))