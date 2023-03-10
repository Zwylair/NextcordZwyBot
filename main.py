from typing import Literal
import sqlite3
import nextcord.ext.commands

from settings import *
from basic_funcs import is_role_exist, is_message_exist

from verifier.verifier_view import VerifierEmbedView, VerifierView
from verifier.verifier_emoji import VerifierEmbedEmojiView, VerifierCogListener
from mafia import MafiaLobbyView
from backgrounds import start_keeping

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
        data: tuple[str, int, int, int, int]
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


bot.run(TOKEN)
