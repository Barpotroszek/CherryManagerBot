import discord
from discord.ext import commands
from discord.ext.commands.errors import RoleNotFound


class RolesManagement(commands.Cog, name="RolesManagement"):
    def __init__(self, bot) -> None:
        self.emoji_raised_hand = "🖐🏼"
        self.emoji_t = "🇹"
        self.emoji_n = "🇳"

        self.emojis = [self.emoji_n, self.emoji_t, self.emoji_raised_hand]
        self.bot = bot

    def get_member(self, guild_id, member_id):
        guild =self.bot.get_guild(guild_id)
        print(guild.members)
        for member in guild.members:
            print(member)
            if member.id == member_id:
                return member

    @commands.group(usage="<option>", invoke_without_subcommand=True)
    async def role(self, ctx):
        """Zarządzanie rolami"""
        if ctx.invoked_subcommand == None:
            await ctx.invoke(self.bot.get_command("help"), "role")

    @role.command(usage="<role> <user1> <user2>...", help="Przydzielanie roli użytkownikom")
    async def give(self, ctx, role: discord.Role, users: commands.Greedy[discord.User]):
        """Przydzielanie roli podanym użytkownikom"""
        for user in users:
            await user.add_roles(role)

        if ctx == None:
            return

        await ctx.send("*Rola została przydzielona*")

    @role.command(usage="<role1> ...")
    async def remove(self, ctx, roles: commands.Greedy[discord.Role]):
        """Usuwanie podanych ról roli"""
        for role in roles:
            try:
                await role.delete()
            except RoleNotFound:
                pass
        await ctx.send("***Role zostały usunięte***")

            # await user.send(cache)
            # await message.channel.send(info)

        # await role_congfirm.send(f"dane z tamtej wiad:")
        # await role_congfirm.send(f"role_id: {role_id}\nmsg_id: {msg.id}")


def setup(bot):
    bot.add_cog(RolesManagement(bot))
