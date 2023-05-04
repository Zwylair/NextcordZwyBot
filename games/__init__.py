import games.hide_and_seek
import games.mafia


def setup(bot):
    bot.add_cog(games.hide_and_seek.HideNSeek(bot))
    bot.add_cog(games.mafia.MafiaCog(bot))
