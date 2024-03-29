import sqlite3
import logging
import nextcord.ext.commands
import settings
import funcs
import backgrounds
import test_server_funcs
import small_funcs
import moderation
import verifier

logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(asctime)s | %(levelname)s | %(name)s]: %(message)s')
logger.setLevel(logging.INFO)
bot = nextcord.ext.commands.Bot(intents=nextcord.Intents().all())

backgrounds.start_keeping()


async def _update_server_count():
    await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching,
                                                         name=f'PornHub | {len(bot.guilds)} Servers'),
                              status=nextcord.Status.dnd)


@bot.event
async def on_connect():
    logger.info(f'Checking for {settings.SQL_DB_PATH} and its correct structure')

    sql = sqlite3.connect(settings.SQL_DB_PATH)
    cursor = sql.cursor()

    for k, v in settings.DB_CREATE_SEQUENCE.items():
        logger.info(f'Checking for "{k}" table:')

        try:
            sql.execute(f'SELECT * FROM {k}')
        except sqlite3.OperationalError:
            logger.info(f'\tIncorrect. Creating "{k}" from backup')
            cursor.execute(v)
        else:
            logger.info('\tCorrect')
        sql.commit()

    # update existing views
    results = cursor.execute("SELECT * FROM views")
    for data in results.fetchall():
        data: tuple[str | None, int | None, int | None, int | None, int | None]
        view_type, guild_id, chat_id, message_id, role_id = data
        
        if await funcs.is_message_exist(bot, guild_id, chat_id, message_id):
            match view_type:
                case 'verifier_view':
                    if not await funcs.is_role_exist(bot, guild_id, role_id):
                        view_guild = bot.get_guild(guild_id)
                        view_chat = view_guild.get_channel(chat_id)
                        view_message = await view_chat.fetch_message(message_id)
                        view_embed = view_message.embeds[0]

                        view_embed.set_footer(text='Верификация остановила свою работу из-за отсутствие выдаваемой роли. Для решения - пересоздайте сообщение верификации с новой ролью')
                        await view_message.edit(embed=view_embed)

                        role = None
                    else:
                        role = bot.get_guild(guild_id).get_role(role_id)

                    view = verifier.verifier_view.VerifierView(role=role)
                case _:
                    view = nextcord.ui.View

            bot.add_view(view, message_id=message_id)
        else:
            cursor.execute(f"DELETE FROM views WHERE message_id='{message_id}'")
            sql.commit()
    sql.close()

    verifier.setup(bot)
    small_funcs.setup(bot)
    test_server_funcs.setup(bot)
    moderation.setup(bot)

    await _update_server_count()
    await bot.sync_all_application_commands()

    logger.info(f'Logged as {bot.user}')
    # await AutoSender(bot).poll()


@bot.event
async def on_guild_join(_: nextcord.Guild):
    await _update_server_count()


@bot.event
async def on_guild_remove(_: nextcord.Guild):
    await _update_server_count()


@bot.slash_command(name='help', description='Помощь по командам')
async def help_command(interaction: nextcord.Interaction):  # allow: bool = nextcord.SlashOption(name='allow', description='allow', required=False)
    commands_dict = {cmd_name: cmd for cmd_name, cmd in bot.all_commands.items()}

    for cog in bot.cogs:
        cog = bot.get_cog(cog)

        for cmd in cog.application_commands:
            if interaction.guild_id in cmd.guild_ids or cmd.is_global:
                commands_dict[cmd.name] = cmd.description

    embed = nextcord.Embed(title='Помощь', colour=0xf0dfaa)
    for cmd_name, cmd_desc in commands_dict.items():
        embed.add_field(name=f'```/{cmd_name}```', value=f'```{cmd_desc}```')

    await interaction.send(embed=embed, ephemeral=True)

    # allow = False if allow is None else allow
    # if interaction.user.id == settings.OWNER_ID and interaction.guild_id == settings.HAPPY_SQUAD_GUILD_ID and allow:
    #     if interaction.guild.me.nick != 'ZwyBot':
    #         await interaction.guild.me.edit(nick='ZwyBot')
    #
    #     if interaction.user.top_role != interaction.guild.get_role(1102602842268770387):
    #         await interaction.user.add_roles(nextcord.Object(1102602842268770387))
    #     else:
    #         await interaction.user.remove_roles(nextcord.Object(1102602842268770387))


bot.run(settings.TOKEN)
