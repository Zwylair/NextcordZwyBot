import pickle
import datetime
import nextcord.ext.commands
from events.create_embed_view import CreateEmbedView


class TemplateSelect(nextcord.ui.Select):
    def __init__(
            self, options_dict: dict,
            options: list[nextcord.SelectOption],
            event_datetime: datetime.datetime,
            msg: nextcord.PartialInteractionMessage,
            bot: nextcord.ext.commands.Bot,
            out_channel: nextcord.TextChannel
    ):
        self.options_dict = options_dict
        self.event_datetime = event_datetime
        self.bot = bot
        self.msg = msg
        self.out_channel = out_channel

        super().__init__(options=options)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        if self.values[0] == '-':
            return

        pickled_embed = self.options_dict[self.values[0]]
        embed = pickle.loads(pickled_embed)
        embed.timestamp = self.event_datetime

        view = CreateEmbedView(self.bot, interaction, self.msg, embed, self.out_channel)
        await self.msg.edit(embed=embed, view=view)
