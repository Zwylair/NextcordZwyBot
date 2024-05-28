import json
from dataclasses import dataclass
import nextcord
import db


@dataclass
class DeleteOptions:
    NOBODY_IN_VOICE = 1
    LOCALIZATION = {
        NOBODY_IN_VOICE: 'Никого в гс',
    }


@dataclass
class ActionWithUsers:
    ADD = 1
    REMOVE = 2


@dataclass
class PrivateVCConfig:
    user_id: int
    people_limit: int | None
    allowed_members: list[nextcord.Member]
    delete_option: int
    vc_name: str

    @staticmethod
    def fetch(user: nextcord.User | nextcord.Member):
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM private_vc_user_config WHERE user_id=?',
            (user.id,)
        )
        res = cur.fetchone()
        cur.close()
        conn.close()

        config = PrivateVCConfig(user.id, None, [user.guild.get_member(user.id)], DeleteOptions.NOBODY_IN_VOICE, '')

        if res is None:
            config.set_vc_name_to_default()
        else:
            config.people_limit = res[1]
            config.allowed_members = [user.guild.get_member(i) for i in json.loads(res[2])]
            config.delete_option = res[3]
            config.vc_name = res[4]

        return config

    def dump(self):
        author = self.allowed_members[0]
        allowed_members_ids = [i.id for i in self.allowed_members]
        allowed_members_ids = json.dumps(allowed_members_ids)

        conn = db.get_conn()
        cur = conn.cursor()

        cur.execute(
            'SELECT user_id FROM private_vc_user_config WHERE user_id=?',
            (author.id,)
        )
        res = cur.fetchone()

        if res is None:  # there are no settings, creating them
            cur.execute(
                'INSERT INTO private_vc_user_config VALUES (?, ?, ?, ?, ?)',
                (author.id, self.people_limit, allowed_members_ids, self.delete_option, self.vc_name)
            )
        else:  # there are settings, update them
            cur.execute(
                'UPDATE private_vc_user_config SET people_limit=?, allowed_members=?, delete_option=?, vc_name=?',
                (self.people_limit, allowed_members_ids, self.delete_option, self.vc_name)
            )

        conn.commit()
        cur.close()
        conn.close()

    def set_vc_name_to_default(self):
        # user.nick is server name of user. using default name if not set
        author = self.allowed_members[0]
        author_name = author.global_name if author.nick is None else author.nick
        self.vc_name = f'{author_name}\'s channel'
