from typing import Literal
import datetime
import nextcord
from nextcord.ext import commands
from settings import *
from metacore.db import EVENT_DICT


class MetacoreCommandsCog(commands.Cog):
    def __init__(self):
        self.count = 0

    @nextcord.slash_command(name='create_event', description='Создать событие', guild_ids=[TEST_GUILD_ID, METACORE_GUILD_ID])
    async def create_event(self, interaction: nextcord.Interaction,
                           event_embed_type: Literal['bunker', 'mafia', 'among us', 'minecraft uhc', 'dota 2 role close', 'zxc metacore', 'karaoke', 'cs role close'] = nextcord.SlashOption(name='event_type', description='Событие', required=True),
                           day: Literal['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] = nextcord.SlashOption(name='day', description='День проведения ивента', required=True),
                           time: str = nextcord.SlashOption(name='time', description='Время проведения ивента (например 21:00)', required=True),
                           url: str = nextcord.SlashOption(name='url', description='Доп. ссылка на то, что должно меняться в евенте', required=False)):
        if interaction.guild.get_role(EVENT_CREATOR_ROLE_ID) not in interaction.user.roles:
            await interaction.send('У вас недостаточно прав для создания события! (Роль)', ephemeral=True)
            return

        input_day_num = {v: k for k, v in DATETIME_WEEKDAY_DICT.items()}[day]
        today_num = datetime.date.today().weekday()

        # Ебать сложные махинации с датой я сделал нахуй, я рот ебал нахуй этой хуйни блядота ёбаная
        interval = input_day_num - today_num if today_num < input_day_num else 7 - today_num + input_day_num
        interval = 0 if interval == 7 else interval
        hour, minute = [int(i) for i in time.split(':')]
        date_now = datetime.datetime.utcnow()
        date_now = date_now.replace(hour=hour, minute=minute)
        timestamp = date_now + datetime.timedelta(days=interval)

        embed: nextcord.Embed = EVENT_DICT[event_embed_type]
        embed.timestamp = timestamp
        
        if EVENT_DICT['cs role close'] == embed:
            if url is None:
                await interaction.send('Отсутствует ссылка на регистрацию в турике!', ephemeral=True)
                return

            desc = embed.description.split('\n')
            desc[-1] = f'⠀⠀⠀⠀⠀⠀⠀⠀⠀[Ссылка на регистрацию на турнир]({url})'
            embed.description = desc

        channel = interaction.guild.get_channel(METACORE_EVENT_CHANNEL_ID)

        event_message = await channel.send(embed=embed)
        await interaction.send(f'Готово! [Отправленное сообщение...]({event_message.jump_url})', ephemeral=True)
