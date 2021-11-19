import discord
from discord import Embed
from discord.ext import commands
from config.config import cache
from config.core import GuildParams


class RoleOnReaction:
    async def ask_for_role(self, payload):
        '''Wywowyławana, gdy ktoś poprosi o rolę'''
        guild = self.bot.get_guild(payload.guild_id)
        message = await guild.get_channel(
            payload.channel_id).fetch_message(payload.message_id)
        user = payload.member

        role_confirm_channel_id = GuildParams(guild.id).role_confirm_channel_id
        role_confirm_channel = self.bot.get_channel(role_confirm_channel_id)

        role_embd = message.embeds[0].to_dict()

        # przyznawanie roli użytkownikom
        '''role_id = int(role_embd["footer"]['text'])'''
        # await role_confirm_channel.send(role_embd)   -> aktualnie niepotrzebne

        ''' TYMCZASOWE ROZWIĄZANIE -> na przyjmowanie organizatorów'''
        role_id = int(role_embd["fields"][1]["value"][3:-1])

        emb = Embed(
            title=f"Prośba użytkownika `{user.name}` o zatwierdzenie roli",
            color=discord.Color.darker_grey()
        )
        emb.add_field(name="Użytkownik:", value=user)
        emb.add_field(name="ID użytkownika:", value=user.id)
        emb.add_field(name="Nazwa roli:", value=guild.get_role(role_id))
        emb.add_field(name="ID roli:", value=guild.get_role(role_id).id)
        emb.add_field(name="Status:", value="Oczekujące", inline=False)
        return await role_confirm_channel.send(embed=emb)

    async def decision_about_role(self, payload, switch):
        guild = self.bot.get_guild(payload.guild_id)
        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        user = payload.member

        emb = message.embeds[0]
        info = emb.to_dict()
        value = int(info["fields"][1]["value"])
        target = await guild.fetch_member(value)
        # await user.send(info)

        # prośba została zaakceptowana
        if switch:
            await target.send(f"Prośba o rolę *`{info['fields'][2]['value']}`* została zaakceptowana!")
            info['fields'][len(
                info['fields'])-1]['value'] = f"Prośba zaakceptowana przez {user.mention}"
            color = discord.Color.green()

            role = guild.get_role(int(info['fields'][3]['value']))

            # przyznanie roli danemu członkowi
            await target.add_roles(role)

        # prośba została odrzucona
        else:
            try:
                await target.send(
                    f"Prośba o rolę *`{info['fields'][2]['value']}`* została odrzucona...\n   to nie moja wina... ja tu tylko sprzątam..."
                )
            except AttributeError as e:
                await message.reply(f"{e.args}, {info}")
                return

            info['fields'][len(
                info['fields'])-1]['value'] = f"Prośba odrzucona przez {user.mention}"
            # await message.channel.send(f"Rola nie została przyznana")
            color = discord.Color.red()

        emb = Embed.from_dict(info)
        emb.colour = color
        await message.edit(embed=emb)
        await message.clear_reactions()


class Moderation:
    async def alert(self, msg):
        print("ALERT")

        moderation_channel_id = GuildParams(
            msg.guild.id).moderation_channel_id

        if moderation_channel_id == None:
            await self.bot.invoke(self.bot.get_command("beginning"))

        moderation_channel_id = GuildParams(
            msg.guild.id).moderation_channel_id
        moderation_channel = msg.guild.get_channel(moderation_channel_id)

        emb = discord.Embed(
            title="`Alert moderatorski` (xd)",
            # colour=0x8b0000,
            author="Monitoring"
        )
        emb.add_field(name="Użytkownik:", value=msg.author)
        emb.add_field(name="ID Użytkownika:", value=msg.author.id)
        emb.add_field(name="Kanał", value=msg.channel.mention)
        emb.add_field(name="Link do wiadomości:", value=msg.jump_url)
        emb.add_field(name="Data wysłania:",
                      value=msg.created_at.strftime("%H:%M %d/%m/%Y"))
        emb.add_field(name="Treść:", value=msg.content, inline=False)

        emb.add_field(name="Status:", value="Do rozpatrzenia")
        emb.add_field(name="Wybierz jedną z opcji działania:",
                      value=f"""{self.emoji_warning} -> wysłanie ostrzeżenia do użytkownika\n
                        {self.emoji_ban} -> nakładanie bana na użytkownika""")

        msg = await moderation_channel.send(embed=emb)
        await msg.add_reaction(self.emoji_warning)
        await msg.add_reaction(self.emoji_ban)

    async def send_warning(self, payload):
        '''Wysyłanie ostrzeżenia do użytkownika'''
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        info = msg.embeds[0].to_dict()

        value = int(info["fields"][1]["value"])
        link = info['fields'][3]["value"]
        target = await guild.fetch_member(value)

        await target.send(
        f"""Joł, mordeczko, w sprawie tej wiadomości:\n {link}
        Zależy mi, żeby na tej grupie była wzajemna życzliwość, także proszę, bez takich sytuacji na przyszłość :wink:. Jeśli to się powtórzy, to prawdopodobnie zostaniesz zbanowany, a może i wyrzucony z tego serwera.
        """)
        info['fields'].pop(len(info['fields'])-1)
        info['fields'][len(info['fields'])-1]['value'] = f"Wysłano ostrzeżenie, {payload.member.mention}"
        emb = Embed.from_dict(info)
        emb.colour = discord.Color.from_rgb(255, 178, 0)
        await msg.edit(embed=emb)
        await msg.clear_reactions()

#@commands.has_any_role("Administracja")
class Listeners(commands.Cog, RoleOnReaction, Moderation):
    '''DO NASŁUCHIWANIA'''    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.prohibited_words = [
            "kurw",
            "pierdo",
            "jeb",
            "spierd"
        ]
        self.emoji_warning = '⚠️'  # ostrzeżenie
        self.emoji_ban = '🚫'  # ban

        self.emoji_raised_hand = "🖐🏼"
        self.emoji_t = "🇹"
        self.emoji_n = "🇳"

        self.role_emojis = [self.emoji_n, self.emoji_t, self.emoji_raised_hand]

    @commands.Cog.listener(name="on_message")
    async def catch_prohibited_words(self, msg):
        if msg.author.id == self.bot.user.id or type(msg.channel) != discord.TextChannel:
            print("Returned")
            return
        print(msg.content)

        '''  MODERACJA  '''
        # jeżeli wyłapano "Zakazane słowa"
        if any(word in msg.content for word in self.prohibited_words):
            await self.alert(msg)

        # jeżeli wiadomość została wysłana przez bota lub na jakimś serwerze
        elif type(msg.channel) == discord.DMChannel:
            # do zrobienia
            try:
                cache['DMessages'].pop(msg.author.id)
            except IndexError:
                pass
            await msg.channel.send("Wiadomość przekazana. Miłego dnia :smiley:")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.id == self.bot.user.id:
            print("bot dał reakcje")
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild == None:
            print("None guild")
            return

        message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        print(message)
        print(payload.emoji.name)

        ''' ZARZĄDZANIE ROLAMI '''
        if payload.emoji.name in self.role_emojis:
            print("HERE BOY")
            # gdy reakcja została dodana na kanale "role"
            if GuildParams(guild.id).role_channel_id == message.channel.id and payload.emoji.name == self.emoji_raised_hand:
                print("I'm here")
                msg = await self.ask_for_role(payload)
                await msg.add_reaction(self.emoji_t)
                await msg.add_reaction(self.emoji_n)

            # gdy reakcja została dodana na kanale przeznaczonym do zatwierdzania ról
            elif GuildParams(guild.id).role_confirm_channel_id == message.channel.id:
                if payload.emoji.name == self.emoji_n:  # wniosek odrzucony
                    await self.decision_about_role(payload, 0)
                elif payload.emoji.name == self.emoji_t:  # wniosek zatwierdzony
                    await self.decision_about_role(payload, 1)

        '''  MODERACJA  '''
        if GuildParams(payload.guild_id).moderation_channel_id == payload.channel_id:
            print("MODERACJA")
            if payload.emoji.name == self.emoji_warning:
                await self.send_warning(payload)


                

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        if (type(channel) == discord.DMChannel) and (user.id not in cache['DMessages']):
            cache['DMessages'].append(user.id)
            print("Użytkownik dodany do listy")
            await user.send("Pamiętaj, że jestem tylko botem. Prawdopodobnie ta wiadomość zostanie przekazana do admistracji :innocent:")


def setup(bot):
    bot.add_cog(Listeners(bot))