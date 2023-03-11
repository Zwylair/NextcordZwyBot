from typing import Literal
import datetime
import sqlite3
import nextcord.ext.commands
from settings import *
from basic_funcs import is_role_exist, is_message_exist
from backgrounds import start_keeping
from verifier.verifier_view import VerifierEmbedView, VerifierView
from verifier.verifier_emoji import VerifierEmbedEmojiView, VerifierCogListener
from mafia import MafiaLobbyView
from metacore.db import EVENT_DICT

bot = nextcord.ext.commands.Bot(intents=nextcord.Intents().all())
start_keeping()


async def _update_server_count():
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching,
                                                         name=f'PornHub | {len(bot.guilds)} Servers'),
                              status=nextcord.Status.dnd)


@bot.event
async def on_connect():
    sql = sqlite3.connect('db.sql')

    # update existing views
    results = sql.execute("SELECT * FROM views")
    for data in results.fetchall():
        data: tuple[str | None, int | None, int | None, int | None, int | None]
        view_type, guild_id, chat_id, message_id, role_id = data
        
        if await is_message_exist(bot, guild_id, chat_id, message_id):
            match view_type:
                case 'verifier_view':
                    if not await is_role_exist(bot, guild_id, role_id):
                        view_guild = bot.get_guild(guild_id)
                        view_chat = view_guild.get_channel(chat_id)
                        view_message = await view_chat.fetch_message(message_id)
                        view_embed = view_message.embeds[0]

                        view_embed.set_footer(text='Верификация остановила свою работу из-за отсутствие выдаваемой роли. Для решения - пересоздайте сообщение верификации с новой ролью')
                        await view_message.edit(embed=view_embed)
                        
                        role = None
                    else:
                        role = bot.get_guild(guild_id).get_role(role_id)

                    view = VerifierView(role=role)
                case _:
                    view = nextcord.ui.View
    
            bot.add_view(view, message_id=message_id)
        else:
            sql.execute(f"DELETE FROM views WHERE message_id='{message_id}'")
            sql.commit()

    sql.close()
 
    bot.add_cog(VerifierCogListener(bot))

    await _update_server_count()
    await bot.sync_all_application_commands()

    print(f'Logged as {bot.user}')


@bot.event
async def on_guild_join(_: nextcord.Guild):
    await _update_server_count()


@bot.event
async def on_guild_remove(_: nextcord.Guild):
    await _update_server_count()


@bot.slash_command(name='help', description='Помощь по командам')
async def help(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title='Помощь', colour=0xf0dfaa)
    for command in bot.get_application_commands():
        embed.add_field(name=f'```/{command.name}```', value=f'```{command.description}```')

    await interaction.send(embed=embed, ephemeral=True)


@bot.slash_command(name='verifier', description='Создать сообщение верификации')
async def verifier(interaction: nextcord.Interaction,
                   target_chat: nextcord.TextChannel = nextcord.SlashOption(name='target_chat', description='Чат, в который будет отослано сообщение', required=True),
                   verification_type: Literal['button', 'emoji'] = nextcord.SlashOption(name='verification_type', description='Тип верификации', required=True)):
    verification_type = 'view' if verification_type == 'button' else verification_type
    embed = nextcord.Embed(title='Title', colour=0x9a72ba, description='Basic Description')
    embed.set_image(VERIFY_BANNER_URL)

    embed_message = await interaction.send(content='Предпоказ сообщения', embed=embed)
    
    match verification_type:
        case 'view':
            await embed_message.edit(embed=embed, view=VerifierEmbedView(bot=bot, base_interaction=interaction, embed_message=embed_message, out_embed=embed, out_chat=target_chat))
        case 'emoji':
            await embed_message.edit(embed=embed, view=VerifierEmbedEmojiView(bot=bot, base_interaction=interaction, embed_message=embed_message, out_embed=embed, out_chat=target_chat))


@bot.slash_command(name='mafia_create_lobby', description='Создать лобби игры "мафия"')
async def create_mafia_lobby(interaction: nextcord.Interaction):
    status_interaction = await interaction.send('Processing', ephemeral=True)
    view = MafiaLobbyView(status_interaction, author=interaction.user)

    await view.update()
    await status_interaction.edit(view=view)


@bot.slash_command(name='create_event', description='Создать событие')
async def create_event(interaction: nextcord.Interaction,
                       event_embed_type: Literal['bunker', 'mafia', 'among us', 'minecraft uhc', 'dota 2 role close', 'zxc metacore', 'karaoke', 'cs role close'] = nextcord.SlashOption(name='event_type', description='Событие', required=True),
                       day: Literal['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] = nextcord.SlashOption(name='day', description='День проведения ивента', required=True),
                       time: str = nextcord.SlashOption(name='time', description='Время проведения ивента (например 21:00)', required=True),
                       url: str = nextcord.SlashOption(name='url', description='Доп. ссылка на то, что должно меняться в евенте', required=False)):
    if interaction.guild_id == METACORE_GUILD_ID:
        if interaction.guild.get_role(EVENT_CREATOR_ROLE_ID) not in interaction.user.roles:
            await interaction.send('У вас недостаточно прав для создания события! (Роль)', ephemeral=True)
            return
    elif interaction.guild_id == TEST_GUILD_ID:
        if interaction.guild.get_role(TEST_EVENT_CREATOR_ROLE_ID) not in interaction.user.roles:
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
    date_now -= datetime.timedelta(hours=2)  # Hot-fix for host
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
    
    channel_id = METACORE_EVENT_CHANNEL_ID if interaction.guild_id == METACORE_GUILD_ID else TEST_METACORE_EVENT_CHANNEL_ID
    channel = interaction.guild.get_channel(channel_id)
    event_message = await channel.send(embed=embed)
    await interaction.send(f'Готово! [Отправленное сообщение...]({event_message.jump_url})', ephemeral=True)


bot.run(TOKEN)
