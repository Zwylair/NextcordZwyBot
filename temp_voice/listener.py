import nextcord.ext.commands
import db


async def setup_listener(bot: nextcord.ext.commands.Bot):
    @bot.event
    async def on_voice_state_update(
            member: nextcord.Member,
            before: nextcord.VoiceState | None,
            _: nextcord.VoiceState | None
    ):
        if before.channel is None:
            return

        channel = member.guild.get_channel(before.channel.id)

        if len(channel.members) > 0:
            return

        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            'SELECT vc_channel_id FROM private_vc WHERE server_id=?',
            (member.guild.id,)
        )

        try:
            expanded_fetch = [i[0] for i in cur.fetchall()]
            expanded_fetch.index(channel.id)
        except ValueError:
            return

        await channel.delete()
        cur.execute(
            'DELETE FROM private_vc WHERE server_id=? AND vc_channel_id=?',
            (member.guild.id, channel.id)
        )

        conn.commit()
        cur.close()
        conn.close()
