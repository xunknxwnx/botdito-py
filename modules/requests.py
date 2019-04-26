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
  async def set(self,ctx,console=None,*,fc=None):
    validconsoles=['3ds','switch']
    consolea=None
    if not console:
      return await ctx.send("You need to provide a console for your friend code!")
    if console.lower() not in validconsoles:
      return await ctx.send("Invalid console. This command is used by doing ``+fc set <console> <fc>``. Valid consoles are ``3ds`` and ``switch``. Please try again.")
    if not fc:
      return await ctx.send("You need to provide your friend code!")
    embed=discord.Embed(description=fc, colour=discord.Colour.blue())
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    channel=discord.utils.get(ctx.guild.channels,name='friend-safari')
    await channel.send(embed=embed)
    if console.lower()=='3ds':
      consolea='ds'
    else:
      consolea=console
    await self.bot.db.execute(f"UPDATE people SET {consolea.lower()}={fc} WHERE user_id={ctx.author.id}")
    await ctx.send("Set your fc! Now you can request Pokemon!")
    
  @fc.command()
  async def view(self,ctx,console=None,user:discord.User=None):
    validconsoles=['3ds','switch']
    consolea=None
    if not user:
      user=ctx.author
    if not console:
      return await ctx.send("You need to provide a console to view a friend code!")
    if console.lower() not in validconsoles:
      return await ctx.send("Invalid console. This command is used by doing ``+fc view <console> @user``. User is optional. Valid consoles are ``3ds`` and ``switch``. Please try again.")
    async with self.bot.db.acquire() as db:
      friendcode=await db.fetchrow(f"SELECT * FROM people WHERE user_id={user.id}")
      if console.lower()=='3ds':
        consolea='ds'
      else:
        consolea=console
      if not friendcode[consolea.lower()]:
        return await ctx.send(f"This user doesn't have an FC set for the {console}!")
      embed=discord.Embed(description=friendcode[consolea.lower()],colour=discord.Colour.blue())
      embed.set_author(name=user.name,icon_url=user.avatar_url)
      await ctx.send(embed=embed)
      await self.bot.db.release(db)
   
  @fc.command()
  async def delete(self,ctx,console=None):
    validconsoles=['3ds','switch']
    consolea=None
    if not console:
      return await ctx.send("You need to provide a console to delete your FC for!") 
    if console.lower() not in validconsoles:
      return await ctx.send("Invalid console. This command is used by doing ``+fcdelete <console>``. Valid consoles are ``3ds`` and ``switch``. Please try again.")
    async with self.bot.db.acquire() as db:
      friendcode=await db.fetchrow(f"SELECT * FROM people WHERE user_id={ctx.author.id}")
      if console.lower()=='3ds':
        consolea='ds'
      else:
        consolea=console
      if not friendcode[consolea.lower()]:
        return await ctx.send("You don't have an FC set for that console!")
      await db.execute(f"UPDATE people SET {consolea.lower()}='' WHERE user_id={ctx.author.id}")
      await ctx.send("Deleted the FC!")
      await self.bot.db.release(db)
      
def setup(bot):
  bot.add_cog(Requests(bot))
