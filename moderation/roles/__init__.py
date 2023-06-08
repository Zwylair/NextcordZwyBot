import nextcord.ext.commands


class RolesModerationCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='role', description='role')
    async def role(self, _: nextcord.Interaction):
        pass

    @role.subcommand(name='give', description='Выдать роль пользователю')
    async def give_role(self, interaction: nextcord.Interaction,
                        member: nextcord.Member = nextcord.SlashOption(name='member', description='Пользователь, которому будет выдана роль'),
                        role: nextcord.Role = nextcord.SlashOption(name='role', description='Роль, которая будет выдана')):
        for user_role in interaction.user.roles:
            if user_role.permissions.manage_roles or user_role.permissions.administrator:
                embed = nextcord.Embed(title='Успех :white_check_mark:', description='Участник успешно изменен!', colour=0x32B76C)

                await member.add_roles(role)
                await interaction.send(embed=embed, ephemeral=True)
                break
        else:
            embed = nextcord.Embed(title='Ошибка! :stop_sign:', description='У вас недостаточно прав! (управление ролями)', colour=0xEC0D6D)
            await interaction.send(embed=embed, ephemeral=True)

    @role.subcommand(name='revoke', description='Забрать роль у пользователя')
    async def revoke_role(self, interaction: nextcord.Interaction,
                          member: nextcord.Member = nextcord.SlashOption(name='member', description='Пользователь, у которого будет забрана роль'),
                          role: nextcord.Role = nextcord.SlashOption(name='role', description='Роль, которая будет забрана')):
        for user_role in interaction.user.roles:
            if user_role.permissions.manage_roles or user_role.permissions.administrator:
                embed = nextcord.Embed(title='Успех :white_check_mark:', description='Участник успешно изменен!', colour=0x32B76C)

                await member.remove_roles(role)
                await interaction.send(embed=embed, ephemeral=True)
                break
        else:
            embed = nextcord.Embed(title='Ошибка! :stop_sign:', description='У вас недостаточно прав! (управление ролями)', colour=0xEC0D6D)
            await interaction.send(embed=embed, ephemeral=True)

    @role.subcommand(name='edit', description='Изменяет указанную роль. Если не желаете менять параметр, пропустите его')
    async def edit_role(self, interaction: nextcord.Interaction,
                        role: nextcord.Role = nextcord.SlashOption(name='role', description='Роль, которая будет изменена'),
                        new_role_name: str = nextcord.SlashOption(name='new_role_name', description='Новое имя роли', default='default', required=False),
                        colour: str = nextcord.SlashOption(name='colour', description='Цвет роли в hex формате, например hex: "#ffffff"', default='default', required=False)):
        for usr_role in interaction.user.roles:
            if usr_role.permissions.manage_roles or usr_role.permissions.administrator:
                
                new_name = new_role_name if new_role_name != 'default' else role.name
                new_colour = int(colour.lstrip("#"), 16) if colour != 'default' else role.colour
                embed = nextcord.Embed(title='Успех :white_check_mark:', description='Роль успешно изменена!', colour=0x32B76C)

                await role.edit(name=new_name, colour=new_colour)
                await interaction.send(embed=embed, ephemeral=True)
                break
        else:
            embed = nextcord.Embed(title='Ошибка! :stop_sign:', description='У вас недостаточно прав! (управление ролями)', colour=0xEC0D6D)
            await interaction.send(embed=embed, ephemeral=True)

    @role.subcommand(name='move', description='Изменяет позицию роли в иерархии')
    async def move_role(self, interaction: nextcord.Interaction,
                        role: nextcord.Role = nextcord.SlashOption(name='role', description='Передвигаемая роль'),
                        new_pos: int = nextcord.SlashOption(name='new_pos', description='Итоговая позиция роли в иерархии')):
        for usr_role in interaction.user.roles:
            if usr_role.permissions.manage_roles or usr_role.permissions.administrator:
                await role.edit(position=new_pos)

                embed = nextcord.Embed(title='Успех :white_check_mark:', description=f'Роль была успешно перемещена!', colour=0x32B76C)
                await interaction.send(embed=embed, ephemeral=True)
                break
        else:
            embed = nextcord.Embed(title='Ошибка! :stop_sign:', description='У вас недостаточно прав! (управление ролями)', colour=0xEC0D6D)
            await interaction.send(embed=embed, ephemeral=True)
