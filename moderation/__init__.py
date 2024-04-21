from moderation.roles import RolesModerationCog
from moderation.small_funcs import SmallModeratorCog


def setup(bot):
    bot.add_cog(RolesModerationCog(bot))
    bot.add_cog(SmallModeratorCog(bot))
