from discord.ext import commands
import discord
from discord.ext.commands.context import Context
from config.core import SERVERS_SETTINGS_FILES, GuildParams, _json, SERVERS_SETTINGS_FILES


class GamesManagement(commands.Cog, name="GamesManagement", ):
    """Zarządzanie grami"""

    def __init__(self, bot):
        self.bot = bot
        self.keys = ['kolor', 'opis', 'guards', 'report']

    def remove_from_list(self, guild_id: int, role_id: int):
        '''Usuwa grę z listy i zwraca wszystkie informacje o niej'''
        data = _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").read()
        to_give = data["games"][str(guild_id)].pop(str(role_id))
        _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").write(data)
        return to_give

    def get_role(self, guild, name):
        for role in guild.roles:
            if role.name == name:
                return role

    def create_embed(self, ctx, role, game_info):
        """ Tworzenie wiadomości typu embed """
        embed = discord.Embed(
            color=game_info['kolor'],
            title=f"***`{role.name}`***"
        )
        grole_id = game_info['guard_role_id']
        grole = ctx.guild.get_role(game_info['guard_role_id'])
        guards = [grole.mention]

        '''for member in self.bot.get_all_members():
            if grole_id in [x.id for x in member.roles]:
                guards.append(member.mention)'''

        # guards = [self.bot.get_user(x).mention for x in game_info['guard_role_id']]
        guards = ", ".join(guards)
        guards = "Aktualnie brak" if guards == "" else guards

        embed.add_field(name="Opis", value=game_info['opis'], inline=False)
        embed.add_field(name="Odpowiedzialni", value=guards, inline=False)
        embed.add_field(name="Zgłoszenia", value=game_info['report'], inline=False)
        embed.set_footer(text=str(role.id))
        return embed

    async def update_message(self, ctx, role, game_info):
        # pobieranie ustawionego kanału na role
        rid = GuildParams(ctx.guild.id).role_channel_id
        message = await self.bot.get_channel(rid).fetch_message(game_info['msg_id'])
        await message.edit(embed=self.create_embed(ctx, role, game_info))

    @commands.group(name="game", usage="<option>")
    async def game(self, ctx):
        """Zarządzanie grami"""
        await ctx.invoke(self.bot.get_command("help"), "game")

    @game.command(name="add", usage = "add <name> <color_in_hex>", help="Dodawanie nowej gry")
    async def add(self, ctx, role_name, color: str, opis=None, report=None):
        """Dodawanie nowej gry:
            <role_name> -> nazwa danej gry i roli
            <kolor> -> kolor danej gry i roli
            <opis> -> opis gry
            <guards> -> odpowiedzialni za daną strefę
            <report> -> link do zgłoszeń
        """

        async with ctx.typing():
            guild_id = str(ctx.guild.id)
            data = _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").read()

            try:
                role_ch = ctx.guild.get_channel(
                    GuildParams(guild_id).role_channel_id)
                if role_ch == None:
                    raise NameError
            except:
                return await ctx.send("Najpierw użyj komendy `!beginning`")

            if role_name in data["games"]:
                try:
                    role = await commands.RoleConverter().convert(ctx, role_name)
                    return await ctx.send("Rola: " + role.mention + " została już utworzona")
                except:
                    data["games"].pop(role_name)


            guild = ctx.guild

            perm_n = discord.PermissionOverwrite()
            perm_n.read_message_history = True
            perm_n.send_messages = False
            perm_n.read_messages = False

            # read only
            perm_r = discord.PermissionOverwrite()
            perm_r.read_message_history = True
            perm_r.read_messages = True
            perm_r.send_messages = False

            # read write only
            perm_rw = discord.PermissionOverwrite()
            perm_rw.read_message_history = True
            perm_rw.read_messages = True
            perm_rw.send_messages = False
            perm_rw.connect = True
            perm_rw.speak = True
            perm_rw.stream = True
            perm_rw.send_messages = True


            # tworzenie koloru
            if color.startswith("#"):
                color = color[1:]
            color = int("0x"+color, 16)
            #color = hex(color)
            
            # overwrite = discord.PermissionOverwrite(read_messages=True, send_messages = True, connect=True)
            role = await ctx.guild.create_role(name=role_name, colour=color)
            guard_role = await ctx.guild.create_role(name=role_name+" Guard🔧", colour=color)

            category = await guild.create_category(role_name)
            await category.set_permissions(target=role, overwrite=perm_rw)

            channels = {
                "🔧organizacyjne": ["txt", perm_n, perm_n],
                "✅taski": ["txt", perm_n, perm_n],
                "🤔pomysły": ["txt", perm_n, perm_n],
                "📜regulamin": ["txt", perm_r, perm_r],
                "📅rozgrywki": ["txt", perm_r, perm_r],
                "❗ważne": ["txt", perm_r, perm_r],
                "❓pytania": ["txt", perm_rw, perm_r],
                "general": ["txt", perm_rw, perm_r],
                "👀spectators": ["txt", perm_rw, perm_rw],

                "🔧 organizacyjne": ["v", perm_n, perm_n],
                "👀 spectators": ["v", perm_rw, perm_rw],
            }

            ch_id = []

            r_spectator = self.get_role(guild, "👀spectator")
            for ch, (type, perm_p, perm_e) in channels.items():
                #perm_player, perm_everyone
                channel = None
                if type=="txt":
                    channel = await category.create_text_channel(ch)
                elif type=='v':
                    channel = await category.create_voice_channel(ch)
                await channel.set_permissions(target=guard_role, overwrite=perm_rw)
                await channel.set_permissions(target=role, overwrite=perm_p)
                await channel.set_permissions(target=r_spectator, overwrite=perm_e)
                ch_id.append(channel.id)

            
            # for ch, perm in voice_channels.items():

            ch_id.append(category.id)

            game_info = {
                "title": role_name,
                "guard_role_id": guard_role.id,
                "kolor": color,
                "opis": opis,
                "report": report,
                "channels": ch_id
            }

            msg = await role_ch.send(embed=self.create_embed(ctx, role, game_info))
            await msg.add_reaction("🖐🏼")
            game_info['msg_id'] = msg.id
            
            data[guild_id][role.id] = game_info
            _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").write(data)
        await ctx.send("***Zrobione!***")

    @game.group(invoke_without_command = True)
    async def update(self, ctx):
        """Aktualizowanie informacji o danej grze"""
        async with ctx.typing():
            channel_id = GuildParams(ctx.guild.id).role_channel_id
            channel = ctx.guild.get_channel(channel_id)
            messages = await channel.history().flatten()
            for msg in messages:
                await msg.add_reaction("🖐🏼")
                #await ctx.send(msg)
            
            data = _json(f"{SERVERS_SETTINGS_FILES}/{ctx.guild.id}.json").read()
            print("Data: \n", data)
            info = data["games"]
            for id in info:
                print(id, info[id])
                role = ctx.guild.get_role(int(id))
                emb = self.create_embed(ctx, role, info[id])
                channel = self.bot.get_channel(GuildParams(ctx.guild.id).role_channel_id)
                msg = await channel.fetch_message(info[id]['msg_id'])
                await msg.edit(embed=emb)
        
        await ctx.send("Powinno być git")

    @update.command(usage="<role> <color>")
    async def color(self, ctx, role: discord.Role, value: str):
        """Aktualizowanie koloru danej roli i gry"""
        async with ctx.typing():
            guild_id = str(ctx.guild.id)
            data = _json(f"{SERVERS_SETTINGS_FILES}/{ctx.guild.id}.json").read()
            game_info = data["games"][str(role.id)]

            
            # tworzenie koloru
            if value.startswith("#"):
                color = value[1:]
            value = int("0x"+color, 16)

            await role.edit(colour=value)


            '''elif type(value) in [discord.user.ClientUser, discord.member.Member ]:
                value = value.id'''

            game_info['kolor'] = value

            # edycja wiadomości embed dotyczącej danej gry
            # pobieranie ustawionego kanału na role
            rid = GuildParams(ctx.guild.id).role_channel_id
            message = await self.bot.get_channel(rid).fetch_message(game_info['msg_id'])
            await message.edit(embed=self.create_embed(ctx, role, game_info))

            data[guild_id][role.id] = game_info
            _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").write(data)

        await ctx.send(f"Rola: ***" + role.mention + "*** została zaktualizowana")

    @update.command(usage="<role> <opis>", help="Aktualizowanie opisu danej gry")
    async def desc(self, ctx, role: discord.Role, opis: str):
        async with ctx.typing():
            guild_id = str(ctx.guild.id)
            data = _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").read()
            game_info = data["games"][str(role.id)]
            game_info['opis'] = opis

            # pobieranie ustawionego kanału na role
            rid = GuildParams(ctx.guild.id).role_channel_id
            message = await self.bot.get_channel(rid).fetch_message(game_info['msg_id'])
            await message.edit(embed=self.create_embed(ctx, role, game_info))

            data[guild_id][role.id] = game_info
            _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").write(data)
        await ctx.send("*Opis został zaktualizowany :D*")

    @update.command(usage="<role>", help="*No aktualnie nie działa jak powinno* :sweat_smile:")
    async def guards(self, ctx, role: discord.Role):
        async with ctx.typing():
            guild_id = str(ctx.guild.id)
            data = _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").read()
            await ctx.send("Praca w toku")
            game_info = data["games"][str(role.id)]

            # pobieranie ustawionego kanału na role
            rid = GuildParams(ctx.guild.id).role_channel_id
            message = await self.bot.get_channel(rid).fetch_message(game_info['msg_id'])
            await message.edit(embed=self.create_embed(ctx, role, game_info))
            data["games"][str(role.id)] = game_info
            _json(f"{SERVERS_SETTINGS_FILES}/{guild_id}.json").write(data)

        await ctx.send(f"Odpowiedzialni do {role.mention} zostali zaktualizowani")

    @game.command(usage = "<role1> ...", help="Usuwa grę i kanały powiązane z daną rolą")
    async def remove(self, ctx: Context, roles: commands.Greedy[discord.Role]):
        """Usuwa grę i kanały powiązane z daną rolą"""
        with ctx.typing():
            for role in roles:
                role_info = self.remove_from_list(ctx.guild.id, role.id)

                for chid in role_info['channels']:
                    channel = self.bot.get_channel(chid)
                    try:
                        await channel.delete()
                    except:
                        pass
                await ctx.guild.get_role(role_info['guard_role_id']).delete()
                await ctx.guild.get_role(role.id).delete()
                msg = await self.bot.get_channel(GuildParams(ctx.guild.id).role_channel_id).fetch_message(role_info['msg_id'])
                await msg.delete()
        await ctx.send("Powinno być zrobione")
    
    '''
    @update.command(usage = "update add_channel <type txt/v> <name>", help="Dodawanie kanału do grupy")
    async def add_channel(self, ctx, type, name):
        if type=="txt":
            #kanał tekstowy
            pass
        else:
            #kanał tekstowy
            pass'''

    '''@update.error
    async def update_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Podałeś za mało danych")'''

    #@game.error
    #@update.error
    async def game_error(self, ctx, error):
        print(type(error))
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"*Brak wymaganego argumentu*, `{error.args[0]}`")
        else:
            await ctx.send(f"{error.args}")

    @commands.command()
    async def test(self, ctx, *args, **kwargs):
        await ctx.send(args)
        await ctx.send(kwargs)


def setup(bot):
    bot.add_cog(GamesManagement(bot))
