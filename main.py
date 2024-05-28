import asyncio
import os
import logging
import nextcord.ext.commands
import dev_features
import small_funcs
import moderation
import verifier
import temp_voice
import events
from settings import *
import zwyFramework
import funcs
import db

logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(asctime)s | %(levelname)s | %(name)s]: %(message)s')
logger.setLevel(logging.INFO)
bot = nextcord.ext.commands.Bot(intents=nextcord.Intents().all())

logger.info(f'Validating the database')

conn = db.get_conn()
cur = conn.cursor()

if tuple(i.to_string() for i in zwyFramework.get_sqlite_dumps(cur)) != DB_DUMPS:
    do_wipe_storage = input('db dumps doesnt match with saved ones. wipe storage? (y/n): ')
    do_wipe_storage = True if do_wipe_storage.lower() == 'y' else False

    if do_wipe_storage:
        cur.close()
        conn.close()
        os.remove(SQL_DB_PATH)

        conn = db.get_conn()
        cur = conn.cursor()

        # restore tables from saved dumps
        for dump in DB_DUMPS:
            cur.execute(dump)

logger.info('The database was validated')


async def _update_server_count():
    await bot.change_presence(
        activity=nextcord.Activity(
            name=f'/help | {len(bot.guilds)} servers',
            type=nextcord.ActivityType.playing
        ),
        status=nextcord.Status.online
    )


@bot.event
async def on_connect():
    await bot.change_presence(
        activity=nextcord.Activity(
            type=nextcord.ActivityType.streaming,
            name='Starting...'
        ),
        status=nextcord.Status.dnd
    )

    await asyncio.sleep(0.5)

    # connect to existing views
    results = cur.execute('SELECT * FROM views')
    for data in results.fetchall():
        data: tuple[str | None, int | None, int | None, int | None, int | None]
        view_type, guild_id, chat_id, message_id, role_id = data

        if not await funcs.is_message_exist(bot, guild_id, chat_id, message_id):
            cur.execute(f'DELETE FROM views WHERE message_id=?', (message_id, ))
            continue

        view_guild = bot.get_guild(guild_id)
        view_chat = view_guild.get_channel(chat_id)
        view_message = await view_chat.fetch_message(message_id)

        match view_type:
            case 'verifier_view':
                if not await funcs.is_role_exist(bot, guild_id, role_id):
                    view_embed = view_message.embeds[0]
                    view_embed.set_footer(
                        text='Verification was stopped because attached role was deleted. '
                             'Recreate the verification message with a new role for resolving'
                    )

                    await view_message.edit(embed=view_embed)
                    role = None
                else:
                    role = bot.get_guild(guild_id).get_role(role_id)

                view = verifier.verifier_view.VerifierView(role=role)

            case 'create_temp_voice_view':
                view = temp_voice.CreatePrivateVoiceView(bot)
                await view_message.edit(view=view)

            case _:  # plug
                view = nextcord.ui.View

        if view.timeout is None:
            bot.add_view(view)
        else:
            bot.add_view(view, message_id=message_id)

    conn.commit()

    dev_features.setup(bot)
    verifier.setup(bot)
    temp_voice.setup(bot)
    small_funcs.setup(bot)
    moderation.setup(bot)
    events.setup(bot)

    await bot.sync_all_application_commands()
    await _update_server_count()

    logger.info(f'Logged as {bot.user}')


@bot.event
async def on_guild_join(_: nextcord.Guild):
    await _update_server_count()


@bot.event
async def on_guild_remove(_: nextcord.Guild):
    await _update_server_count()


@bot.slash_command(name='help', description='Помощь по командам')
async def help_command(interaction: nextcord.Interaction):
    commands_dict = {cmd_name: cmd.description for cmd_name, cmd in bot.all_commands.items() if cmd.name == cmd.description}

    for cog in bot.cogs:
        cog = bot.get_cog(cog)

        for cmd in cog.application_commands:
            if interaction.guild_id in cmd.guild_ids or cmd.is_global:
                if cmd.name == cmd.description:
                    continue
                commands_dict[cmd.name] = cmd.description

    embed = nextcord.Embed(title='📙 Помощь', colour=0xf9f9f9)
    for cmd_name, cmd_desc in commands_dict.items():
        embed.add_field(name=f'```/{cmd_name}```', value=f'```{cmd_desc}```')

    await interaction.send(embed=embed, ephemeral=True)


bot.run(TOKEN)
