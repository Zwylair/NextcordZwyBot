import nextcord

BUNKER_EMBED = nextcord.Embed(title='ИВЕНТ: БУНКЕР', colour=0xCECECE,
                              description='```Участников метаморфоза встречает новый ивент, а именно симулятор путина под названием "Бункер"\n'
                                          'Вся подробную инфу можно глянуть на сайте где и будет проводиться ивент (сайт находится в строке примечания)```')
BUNKER_EMBED.add_field(name='Для участия нажмите кнопку `УЧАСТВОВАТЬ`', inline=False, value='призом является роль обозначающая вас победителем ивента')
BUNKER_EMBED.add_field(name='Примечание', inline=False, value='Так же ознакомьтесь с [правилами](https://bunker-online.com/rules) игры прежде чем подавать заявку для участия')
BUNKER_EMBED.set_image('https://media.discordapp.net/attachments/345528162668511242/1019663408775299142/72bf95f3e3f19.png?width=500&height=333')
BUNKER_EMBED.set_footer(text='Будет проведено', icon_url='https://media.discordapp.net/attachments/453848841616228354/1019665263320375336/gas-mask.png')

#

MAFIA_EMBED = nextcord.Embed(title='ИВЕНТ: БУНКЕР', colour=0xCECECE,
                             description='```Наконец-то всеми любимая мафия добралась до метаморфоза и встречает участников с распростертыми объятиями в своих рядах. Шлюхи, акробатические номера, клоуны, бассейны из пива и тамада. Этого всего не будет, но зато вас ждет очень атмосферный вечер в компании приятных и не очень приятных лиц которые разделять с тобой игру в мафию. ```')
MAFIA_EMBED.add_field(name='Для участия нажмите кнопку `УЧАСТВОВАТЬ`', inline=False, value='призом является роль обозначающая вас победителем ивента')
MAFIA_EMBED.add_field(name='Примечание', inline=False, value='Так же ознакомьтесь с [правилами](https://kava.ua/news/pravila-igry-v-mafiyu-rolevuyu) игры прежде чем подавать заявку для участия')
MAFIA_EMBED.set_image('https://media.discordapp.net/attachments/345528162668511242/1019663408775299142/72bf95f3e3f19.png?width=500&height=333')
MAFIA_EMBED.set_footer(text='Будет проведено', icon_url='https://media.discordapp.net/attachments/453848841616228354/1018589305150648431/5357ec10fa79e6da.png')

#

AMONGUS_EMBED = nextcord.Embed(title='ИВЕНТ: Among Us', colour=0x5D43F3,
                               description='```Уважаемые граждане метакора, мы рады представить вам второй ивент по игре Among Us\n\n'
                                           'Думаю что правила никому объяснять не нужно, но для тех кто совсем в бункере, то это аналог Мафии с другими правилами и заданиями, по мере выполнения которых на вас будет охотиться импостер, то бишь предатель. Его цель убить всех на борту, ваша - успеть закончить все задания или вычислить цель и выкинуть за борт```')
AMONGUS_EMBED.add_field(name='Для участия нажмите кнопку `УЧАСТВОВАТЬ`', value='призом является роль обозначающая вас победителем ивента')
AMONGUS_EMBED.set_image('https://media.discordapp.net/attachments/453848841616228354/1081355783729590303/Preview13.png?width=500&height=333')
AMONGUS_EMBED.set_footer(text='Будет проведено', icon_url='https://media.discordapp.net/attachments/453848841616228354/1081356023140454420/61d183263a856e0004c6334a.png')

#

MINECRAFT_UHC_EMBED = nextcord.Embed(title='ИВЕНТ: Minecraft Ultra Hardcore ꑭ', colour=0x1C9C04,
                                     description='Доброго вечора ми з Метакору!\n'
                                                 '\n'
                                                 'Будет проведен ивент в Майнкрафте под названием "Metacore UHC" (metacore ultra hardcore), чья суть заключается в хардкорном выживании на ограниченной территории с кастомными правилами и приколами')
MINECRAFT_UHC_EMBED.add_field(name='Правила', inline=False,
                              value='```'
                                    '— игроки играют ТОЛЬКО с модом на войс (Forge | Fabric)\n'
                                    '— в конце должен остаться лишь один (тимиться не запрещено)\n'
                                    '— любые читы - запрещены```\n'
                                    '⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`Приз: уникальная роль и респект+`')
MINECRAFT_UHC_EMBED.set_image('https://media.discordapp.net/attachments/1027282521592971334/1074837122508402858/metacore_uhc_meganasrano_4k_govno.png?width=500&height=333')
MINECRAFT_UHC_EMBED.set_footer(text='Будет проведено', icon_url='https://media.discordapp.net/attachments/1027282521592971334/1064254833705631937/latest.png')

#

DOTA_EMBED = nextcord.Embed(title='ИВЕНТ: DOTA 2 ROLE CLOSE', colour=0xFC1414,
                            description='```Жителям метакора салам, остальным соболезную\n'
                                        '\n'
                                        'Сегодня будет проходить локальный рол клоз 5 vs 5 в игре Dota 2\n'
                                        'Всех желающих ожидаем в сортировочной руме\n'
                                        '\n'
                                        'Правила всем итак известны, а кто забыл - напомню. В начале проходит голосование за один из двух режимов игры\n\n'
                                        '* 1/2 - Составы команд отбираются методом рандома\n'
                                        '* 2/2 - Составы команд заранее отобраны```\n'
                                        '\n'
                                        'После запускается локальное лобби, куда нужно будет присоединиться\n'
                                        '⠀⠀⠀⠀⠀МАКСИМАЛЬНОЕ КОЛИЧЕСТВО МЕСТ ОГРАНИЧЕНО!!!\n'
                                        'призом является роль обозначающая вас победителем ивента')
DOTA_EMBED.set_image('https://media.tenor.com/Us9N0T3M-Z0AAAAC/dota2-%25D0%25B4%25D0%25BE%25D1%2582%25D0%25B02.gif?width=500&height=301')
DOTA_EMBED.set_footer(text='Будет проведено', icon_url='https://media.discordapp.net/attachments/453848841616228354/1018296588776521828/dota2png.png')

#

ZXC_METACORE = nextcord.Embed(title='METACORE ZXC', colour=0x383737,
                              description='Четное кол-во игроков сразятся за звание главного дединсайда Метакора.\n'
                                          '\n'
                                          'Суть ивента: игроки сражаются 1 на 1 на сфах, победит самый безманный. (Кто прочитал как безмамный - долбаеб)\n'
                                          '\n'
                                          'Короче похуй - дата ивента внизу, пингану ивентсабов когда начнем. Нужно будет просто залететь в руму.\n'
                                          '\n'
                                          'Оставляйте реакцию, кому не поебать\n'
                                          '\n'
                                          'Приз: уникальная роль + 2500 тугриков')
ZXC_METACORE.set_image('https://media.discordapp.net/attachments/453848841616228354/1023751745224048680/dota-enigma-enigma-planet.gif?width=500&height=250')
ZXC_METACORE.set_footer(text='Будет проведено')

#

KARAOKE_EMBED = nextcord.Embed(title='Event: Karaoke', colour=0xFFFFFF,
                               description='```"Нино, зайди на метакор, а не пей вино" сказал бы Олег Винник, если бы сидел на нашем сервере. Именно поэтому наша команда объявляет запуск ивента КАРАОКЕ, чтобы на нас обратили внимание именитые певцы и пришли исполнять сюда концерты. А пока их нет нашими артистами будете вы! Да-да, вы не ослышались, именно ты можешь прийти в это прохладное осеннее воскресенье и показать нам свои вокальные способности и заработать тугриков в свою копилочку.\n'
                                           '\n'
                                           'Мы ждем тебя, Винник младший <3```')
KARAOKE_EMBED.set_image('https://media.discordapp.net/attachments/453848841616228354/1038153037824401548/karaoke.png?width=500&height=281')
KARAOKE_EMBED.set_footer(text='Будет проведено', icon_url='https://media.discordapp.net/attachments/453848841616228354/1038157894539018361/56c1a7c57b8595ad.png')

#

CSGO_ROLE_CLOSE_EMBED = nextcord.Embed(title='', colour=0x438FC9,
                                       description='Кто ждал, кто не ждал, но у нас теперь будут клозы по контр стайку, с тем же призовым фондом, что и ранее, а именно роль виннера на метаморфозе.\n'
                                                   '\n'
                                                   'Вы можете зарегистрироваться как и по одиночке, так и зарегистрировать целую команду, можно и не полноценную.\n'
                                                   '\n'
                                                   'Античит Faceit обязателен\n'
                                                   '⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀↓↓↓\n'
                                                   '⠀⠀⠀⠀⠀⠀⠀⠀⠀Ссылка на регистрацию на турнир')
CSGO_ROLE_CLOSE_EMBED.set_image('https://media.discordapp.net/attachments/453848841616228354/1026548996929503302/75ii.gif?width=500&height=368')
CSGO_ROLE_CLOSE_EMBED.set_footer(text='Будет проведено', icon_url='https://media.discordapp.net/attachments/856511610716422144/1026554642517217391/pngegg_1.png')

#

EVENT_DICT = {
    'bunker': BUNKER_EMBED,
    'mafia': MAFIA_EMBED,
    'among us': AMONGUS_EMBED,
    'minecraft uhc': MINECRAFT_UHC_EMBED,
    'dota 2 role close': DOTA_EMBED,
    'zxc metacore': ZXC_METACORE,
    'karaoke': KARAOKE_EMBED,
    'cs role close': CSGO_ROLE_CLOSE_EMBED
}
