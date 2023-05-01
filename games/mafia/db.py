import nextcord
from games.mafia.roles import PlayerRole, Innocent, Mafia, Don, Doctor, Commissar, Bum, Slut, Morph

ROLES_DICT = {'6-6': [Mafia],
              '7-7': [Mafia, Mafia],
              '8-11': [Mafia, Mafia, Don, Doctor, Commissar],
              '12-14': [Mafia, Mafia, Don, Doctor, Commissar, Bum],
              '15-17': [Mafia, Mafia, Don, Doctor, Commissar, Bum, Slut],
              '18-20': [Mafia, Mafia, Don, Doctor, Commissar, Bum, Slut, Morph]}
SECONDARY_ROLES_LIMITS = {Bum: ['12-14', '15-17', '18-20'],
                          Slut: ['15-17', '18-20'],
                          Morph: ['18-20']}


class Player:
    def __init__(self, nextcord_user: nextcord.User | nextcord.Member, role: PlayerRole, interaction_for_answer: nextcord.Interaction):
        self.nextcord_user = nextcord_user
        self.role: PlayerRole = role
        self.interaction_for_answer: nextcord.Interaction = interaction_for_answer
