import nextcord.ext.commands
from temp_voice.classes import *
import db


async def on_voice_state_update(
        member: nextcord.Member,
        _: nextcord.VoiceState | None,
        after: nextcord.VoiceState | None
):
    if after.channel is None:
        return

    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        'SELECT server_id FROM private_vc_server_config WHERE server_id=? AND creator_vc_channel=?',
        (member.guild.id, after.channel.id)
    )

    if cur.fetchone() is None:
        # this channel is not private vc creator
        cur.close()
        conn.close()
        return

    options = PrivateVCConfig.fetch(member)
    vc_permissions = {member.guild.default_role: nextcord.PermissionOverwrite(connect=False)}
    vc_permissions |= {member: nextcord.PermissionOverwrite(connect=True) for member in options.allowed_members}

    private_channel = await after.channel.category.create_voice_channel(
        name=options.vc_name,
        user_limit=options.people_limit,
        overwrites=vc_permissions
    )

    cur.execute(
        'INSERT INTO private_vc VALUES (?, ?, ?)',
        (member.guild.id, private_channel.id, member.id)
    )
    conn.commit()
    cur.close()
    conn.close()

    await member.move_to(private_channel)
