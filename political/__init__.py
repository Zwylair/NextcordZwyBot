import sqlite3
import nextcord.ext.commands
import political.vote
import settings


class PoliticalCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='politics', description='politics')
    async def politics(self, _: nextcord.Interaction):
        pass

    @politics.subcommand(name='create_sql', description='create_sql')
    async def create_sql(self, interaction: nextcord.Interaction):
        sql = sqlite3.connect(settings.SQL_DB_PATH)
        sql.execute("DROP TABLE political")
        sql.commit()
        sql.execute(f"CREATE TABLE political (name varchar(255), desc varchar(255), banner_url varchar(255), popularity int)")
        sql.commit()
        sql.close()

        await interaction.send('p', ephemeral=True)

    @politics.subcommand(name='create_party', description='create_party')
    async def create_party(self, interaction: nextcord.Interaction,
                           name: str = nextcord.SlashOption(name='party_name', description='party_name'),
                           desc: str = nextcord.SlashOption(name='party_desc', description='party_desc'),
                           banner_url: str = nextcord.SlashOption(name='party_banner_url',
                                                                  description='party_banner_url', required=False)):
        banner_url = '' if banner_url is None else banner_url
    
        sql = sqlite3.connect(settings.SQL_DB_PATH)
        sql.execute(f"INSERT INTO political (name, desc, banner_url, popularity) VALUES ('{name}', '{desc}', '{banner_url}', '0')")
        sql.commit()
        sql.close()

        embed = nextcord.Embed(title='Успех', description=f'Партия `{name}` была успешно создана!', colour=0x396ECC)
        await interaction.send(embed=embed, ephemeral=True)

    @politics.subcommand(name='browse', description='browse')
    async def browse(self, interaction: nextcord.Interaction):
        sql = sqlite3.connect(settings.SQL_DB_PATH)
        req = sql.execute("SELECT * FROM political").fetchall()
        sql.close()

        embed = nextcord.Embed(title='Parties 📊', colour=0x396ECC)
        for i in req:
            name, desc, banner_url, popularity = i
            embed.add_field(name=f'`{name} [popularity: {popularity}]`', value=desc)

        await interaction.send(embed=embed, ephemeral=True)

    @politics.subcommand(name='vote', description='vote')
    async def vote(self, interaction: nextcord.Interaction,
                   channel: nextcord.TextChannel = nextcord.SlashOption(name='channel', description='channel'),
                   desc: str = nextcord.SlashOption(name='party_desc', description='party_desc')):
        sql = sqlite3.connect(settings.SQL_DB_PATH)
        req = sql.execute("SELECT * FROM political").fetchall()
        sql.close()

        embed = nextcord.Embed(title='Parties 📊', description=desc, colour=0x396ECC)
        parties = {v[0]: v[3] for v in req}
        view = political.vote.VoteView(self.bot, parties, None, interaction.user)

        embed.add_field(name='none', value='none', inline=False)
        for i in req:
            name, desc, banner_url, popularity = i
            embed.add_field(name=f'`{name}`', value=desc)

            item = ButtonNew(label=name, style=nextcord.ButtonStyle.gray, custom_id=name)
            view.add_item(item)
            view.parties[name] = 0

        status_message = await channel.send(embed=embed)
        view.status_message = status_message
        await view.update()
        await interaction.send('Голосование отправлено!', ephemeral=True)


class ButtonNew(nextcord.ui.Button):
    async def callback(self, interaction: nextcord.Interaction):
        if interaction.user not in self.view.votes.keys():
            self.view.parties[self.label] += 1
            self.view.votes[interaction.user] = self.label

            await interaction.send(f'Вы проголосовали за {self.label}!', ephemeral=True)
        else:
            await interaction.send('Вы уже проголосовали', ephemeral=True)
        await self.view.update()


def setup(bot):
    bot.add_cog(PoliticalCog(bot))
