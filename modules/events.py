import discord
from discord.ext import commands

class Events(commands.Cog, name="Events"):
  def __init__(self, bot):
    self.bot=bot
    
  async def ensure_users(self, user):
    person=await self.bot.db.fetchrow(f"SELECT * FROM people WHERE user_id={user.id}")
    requests=await self.bot.db.fetchrow(f"SELECT * FROM requests WHERE user_id={user.id}")
    if not person:
      await self.bot.db.execute(f"INSERT INTO people(user_id, ds, switch) VALUES({member.id}, '', '')")
    if not requests:
      await self.bot.db.execute(f"INSERT INTO requests(user_id, requests, ongoing) VALUES({member.id}, ARRAY [], ARRAY [])")
  
  @commands.Cog.listener()                       
  async def on_member_join(self,member):
    await self.bot.db.execute(f"INSERT INTO people(user_id, ds, switch) VALUES({member.id}, '', '')")
    await self.bot.db.execute(f"INSERT INTO requests(user_id, requests, ongoing) VALUES({member.id}, ARRAY [], ARRAY [])")
    
  @commands.Cog.listener()
  async def on_member_leave(self,member):
    await self.bot.db.execute(f"DELETE FROM people WHERE user_id={member.id}")
    await self.bot.db.execute(f"DELETE FROM requests WHERE user_id={member.id}")
    
  @commands.Cog.listener()
  async def on_message(self,message):
    await self.ensure_users(message.author)
    
def setup(bot):
  bot.add_cog(Events(bot))
