import discord
from discord.ext import commands

class Requests(commands.Cog, name='Requests'):
  def __init__(self,bot):
    self.bot=bot
    
  @commands.group(name="friendcode",aliases=['fc'])
  async def fc(self,ctx):
    if ctx.invoked_subcommand==None:
      await ctx.send("Command is under construction")
      
  @fc.command()
  async def view(self,ctx,user=None,console=None):
    valid_consoles=['3ds','switch']
    
      
def setup(bot):
  bot.add_cog(Requests(bot))
