import nextcord


class PlayerRole:
    def __init__(self):
        self.desc_embed: nextcord.Embed = nextcord.Embed(colour=0x2596BE, title='```Описание роли```', description='None')


class Innocent(PlayerRole):
    def __init__(self):
        super().__init__()
        self.desc_embed.description = 'Роль, которая не даёт специфичных возможностей'

    def __str__(self):
        return 'Мирный'


class Don(PlayerRole):
    def __init__(self):
        super().__init__()
        self.desc_embed.description = '```Дон - Мафия, которая в придачу может делать проверку игрока на шерифа```'

    def __str__(self):
        return 'Дон'


class Mafia(PlayerRole):
    def __init__(self):
        super().__init__()
        self.desc_embed.description = '```Мафия - Роль позволяющая убивать одного игрока за ночь. Мафии и дон действуют сообща - они должны единогласно выбрать жертву```'
    
    def __str__(self):
        return 'Мафия'


class Doctor(PlayerRole):
    def __init__(self):
        super().__init__()
        self.desc_embed.description = '```Доктор - Роль мирного жителя, позволяющая лечить одного игрока за ночь```'
        self.desc_embed.add_field(name='```Ограничения```', value='```Нельзя лечить одного и того же игрока несколько раз подряд```')

    def __str__(self):
        return 'Доктор'


class Commissar(PlayerRole):
    def __init__(self):
        super().__init__()
        self.desc_embed.description = '```Комиссар - Роль мирного жителя, с помощью которой можно проверить игрока на мафию или дона```'

    def __str__(self):
        return 'Комиссар'


class Morph(PlayerRole):
    def __init__(self):
        super().__init__()
        self.desc_embed.description = '```Морф - Роль мирного жителя. Обладатель роли превращается в мафию после смерти одного из мафий```'

    def __str__(self):
        return 'Морф'


class Slut(PlayerRole):
    def __init__(self):
        super().__init__()
        self.desc_embed.description = '```Ночная бабочка - Роль мирного жителя, которая позволяет отменить действие роли любого игрока```'
        self.desc_embed.add_field(name='```Ограничения```',
                                  value='```1. Ночная бабочка спасает игрока, если тот был атакован этой ночью\n'
                                        '2. Если ночная бабочка забрала доктора, то игрок, к которому шёл доктор **НЕ** будет вылечен```')

    def __str__(self):
        return 'Ночная бабочка'


class Bum(PlayerRole):
    def __init__(self):
        super().__init__()
        self.desc_embed.description = '```Бомж - Роль мирного игрока, которая позволяет узнать имя убийцы игрока, за которым тот следил ночью```'

    def __str__(self):
        return 'Бомж'
