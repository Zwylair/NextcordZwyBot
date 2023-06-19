import games.hide_and_seek
import games.mafia
import games.global_crisis


def setup(bot):
    bot.add_cog(games.hide_and_seek.HideNSeek(bot))
    bot.add_cog(games.mafia.MafiaCog(bot))
    bot.add_cog(games.global_crisis.GlobalCrisis(bot))
