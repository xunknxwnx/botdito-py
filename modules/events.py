import discord
from discord.ext import commands

class Events(commands.Cog, name="Events"):
  def __init__(self, bot):
    self.bot=bot
    
  @commands.Cog.listener()                       
  async def on_member_join(self,member):
    await self.bot.db.execute(f"INSERT INTO people(user_id, ds, switch) VALUES({member.id}, '', '')")
    
  @commands.Cog.listener()
  async def on_member_leave(self,member):
    await self.bot.db.execute(f"DELETE FROM people WHERE user_id={member.id}")
    
def setup(bot):
  bot.add_cog(Events(bot))
