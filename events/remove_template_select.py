import nextcord.ext.commands
import db


class RemoveTemplateSelect(nextcord.ui.Select):
    def __init__(
            self, options_dict: dict, bot: nextcord.ext.commands.Bot,
            msg: nextcord.PartialInteractionMessage
    ):
        self.options_dict = options_dict
        self.msg = msg
        self.bot = bot

        options = []
        for template_name, pickled_embed in options_dict.items():
            options.append(nextcord.SelectOption(label=template_name))

        super().__init__(options=options)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        if self.values[0] == '-':
            return

        msg = await interaction.send('Уверенны, что хотите удалить этот шаблон?', ephemeral=True)
        view = RemoveTemplateButtonsView(bot=self.bot, que=msg, select_object=self)
        await msg.edit(view=view)


class RemoveTemplateButtonsView(nextcord.ui.View):
    def __init__(
            self, bot: nextcord.ext.commands.Bot,
            que: nextcord.PartialInteractionMessage,
            select_object: RemoveTemplateSelect,

    ):
        super().__init__()

        self.bot = bot
        self.que = que
        self.select_object = select_object

    @nextcord.ui.button(label='Удалить', style=nextcord.ButtonStyle.red)
    async def delete(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        with db.get_conn() as conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM event_templates WHERE server_id = ? AND template_name = ?',
                        (interaction.guild_id, self.select_object.values[0]))
            conn.commit()
        await self.que.edit(content=f'{self.select_object.values[0]} был удален', view=None)

        self.select_object.options_dict.pop(self.select_object.values[0])
        options = []
        for template_name, pickled_embed in self.select_object.options_dict.items():
            options.append(nextcord.SelectOption(label=template_name))
        self.select_object.options = options

        view = nextcord.ui.View()
        view.add_item(self.select_object)
        await self.select_object.msg.edit(view=view)

    @nextcord.ui.button(label='Отмена', style=nextcord.ButtonStyle.blurple)
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.que.edit(content='Удаление было отменено', view=None)
