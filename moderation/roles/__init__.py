import nextcord.ext.commands
import nextcord.errors


success_embed = nextcord.Embed(
    title='✅ Успех',
    description='Роль успешно изменена!',
    colour=0x4ee28f
)
error_embed_role_higher = nextcord.Embed(
    title='🛑 Ошибка!',
    description='У меня недостаточно прав! (роль находится выше роли бота)',
    colour=0xf95454
)
error_embed_user_no_permission_role_management = nextcord.Embed(
    title='🛑 Ошибка!',
    description='У вас недостаточно прав! (управление ролями)',
    colour=0xf95454
)
error_embed_bot_no_permission_role_management = nextcord.Embed(
    title='🛑 Ошибка!',
    description='У меня недостаточно прав! (управление ролями)',
    colour=0xf95454
)


async def check_perms(interaction: nextcord.Interaction):
    perms = interaction.guild.me.guild_permissions
    return True if perms.administrator or perms.manage_roles else False


class RolesModerationCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='role', description='role')
    async def role(self, _: nextcord.Interaction):
        pass

    @role.subcommand(name='give', description='Выдать роль пользователю')
    async def give_role(
            self, interaction: nextcord.Interaction,
            member: nextcord.Member = nextcord.SlashOption(
                name='member',
                description='Пользователь, которому будет выдана роль'
            ),
            role: nextcord.Role = nextcord.SlashOption(
                name='role',
                description='Роль, которая будет выдана')
    ):
        if not await check_perms(interaction):
            await interaction.send(embed=error_embed_bot_no_permission_role_management, ephemeral=True)
            return

        for user_role in interaction.user.roles:
            if user_role.permissions.manage_roles or user_role.permissions.administrator:
                try:
                    await member.add_roles(role)
                    await interaction.send(embed=success_embed, ephemeral=True)
                    return
                except nextcord.errors.Forbidden:
                    await interaction.send(embed=error_embed_role_higher, ephemeral=True)
                    return
        else:
            await interaction.send(embed=error_embed_user_no_permission_role_management, ephemeral=True)
            return

    @role.subcommand(name='revoke', description='Забрать роль у пользователя')
    async def revoke_role(self, interaction: nextcord.Interaction,
                          member: nextcord.Member = nextcord.SlashOption(name='member', description='Пользователь, у которого будет забрана роль'),
                          role: nextcord.Role = nextcord.SlashOption(name='role', description='Роль, которая будет забрана')):
        if not await check_perms(interaction):
            await interaction.send(embed=error_embed_bot_no_permission_role_management, ephemeral=True)

        for user_role in interaction.user.roles:
            if user_role.permissions.manage_roles or user_role.permissions.administrator:
                try:
                    await member.remove_roles(role)
                    await interaction.send(embed=success_embed, ephemeral=True)
                    return
                except nextcord.errors.Forbidden:
                    await interaction.send(embed=error_embed_role_higher, ephemeral=True)
                    return
        else:
            await interaction.send(embed=error_embed_user_no_permission_role_management, ephemeral=True)
            return

    @role.subcommand(name='edit', description='Изменяет указанную роль. Если не желаете менять параметр, пропустите его')
    async def edit_role(
            self, interaction: nextcord.Interaction,
            role: nextcord.Role = nextcord.SlashOption(
                name='role',
                description='Роль, которая будет изменена'
            ),
            new_role_name: str = nextcord.SlashOption(
                name='new_role_name',
                description='Новое имя роли',
                default='default',
                required=False
            ),
            colour: str = nextcord.SlashOption(
                name='colour',
                description='Цвет роли в hex формате, например hex: "#ffffff"',
                default='default',
                required=False
            )
    ):
        if not await check_perms(interaction):
            await interaction.send(embed=error_embed_bot_no_permission_role_management, ephemeral=True)
            return

        for usr_role in interaction.user.roles:
            if usr_role.permissions.manage_roles or usr_role.permissions.administrator:
                new_name = new_role_name if new_role_name != 'default' else role.name
                new_colour = int(colour.lstrip("#"), 16) if colour != 'default' else role.colour

                try:
                    await role.edit(name=new_name, colour=new_colour)
                    await interaction.send(embed=success_embed, ephemeral=True)
                    return
                except nextcord.errors.Forbidden:
                    await interaction.send(embed=error_embed_role_higher, ephemeral=True)
                    return
        else:
            await interaction.send(embed=error_embed_user_no_permission_role_management, ephemeral=True)
            return

    @role.subcommand(name='move', description='Изменяет позицию роли в иерархии')
    async def move_role(
            self, interaction: nextcord.Interaction,
            role: nextcord.Role = nextcord.SlashOption(
                name='role',
                description='Передвигаемая роль'
            ),
            new_pos: int = nextcord.SlashOption(
                name='new_pos',
                description='Итоговая позиция роли в иерархии'
            )
    ):
        if not await check_perms(interaction):
            await interaction.send(embed=error_embed_bot_no_permission_role_management, ephemeral=True)
            return

        for usr_role in interaction.user.roles:
            if usr_role.permissions.manage_roles or usr_role.permissions.administrator:
                try:
                    await role.edit(position=new_pos)
                    await interaction.send(embed=success_embed, ephemeral=True)
                    return
                except nextcord.errors.Forbidden:
                    await interaction.send(embed=error_embed_role_higher, ephemeral=True)
                    return
        else:
            await interaction.send(embed=error_embed_user_no_permission_role_management, ephemeral=True)
            return
