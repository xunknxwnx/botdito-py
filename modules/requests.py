import discord, aiohttp
from discord.ext import commands
from urllib.parse import urlparse

class Requests(commands.Cog, name='Requests'):
  def __init__(self,bot):
    self.bot=bot
    
  def chunk(self,l,size):
    for i in range(0,len(l),size):
      yield l[i:i+size]
   
  def pokemon_counter(self,team,string):
    count=0
    thing=team.split("\r\n\r\n")
    for i in thing:
      count+=1
    return count
    
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
    await self.bot.db.execute(f"UPDATE people SET {consolea.lower()}='{fc}' WHERE user_id={ctx.author.id}")
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
      
  @fc.command()
  async def search(self,ctx,console=None,*,username=None):
    validconsoles=['3ds','switch']
    consolea=None
    if not username:
      return await ctx.send("You need to provide a username to search for!")
    if not console:
      return await ctx.send("You need to provide a console to view a friend code!")
    if console.lower() not in validconsoles:
      return await ctx.send("Invalid console. This command is used by doing ``+fc search <console> <username>``. Valid consoles are ``3ds`` and ``switch``. Please try again.")
    members=[i for i in ctx.guild.members if username in i.name or username in i.display_name]
    if not members:
      return await ctx.send("No users found.")
    async with self.bot.db.acquire() as db:
      if console.lower()=='3ds':
        consolea='ds'
      else:
        consolea=console
      people=[]
      for i in members:
        friendcode=await db.fetchrow(f"SELECT {consolea.lower()} FROM people WHERE user_id={i.id}")
        if friendcode[consolea.lower()]:
          people.append(i)
      final=self.chunk(people, 25)
      await ctx.send(final)
      text=""
      index=1
      for i in final:
        text+=f"{index} - {i.name}\n"
        index+=1
      embed=discord.Embed(description=text, colour=discord.Colour.blue())
      msg=await ctx.send(embed=embed)
      await ctx.send("Please select a user by saying a number.")
      def check(m):
        return True if m.author==ctx.author and m.channel==ctx.channel else False
      wait=await self.bot.wait_for('message', check=check)
      num=int(wait.content)
      await ctx.send(final[num-1])
      await self.bot.db.release(db)
      
  @commands.group(name='request')
  async def requests(self,ctx):
    role=discord.utils.get(ctx.guild.roles,name='SnowBuddy')
    if role not in ctx.author.roles:
      return await ctx.send("You need to add your FC. Please set it by doing ``+fc set``")
    async with self.bot.db.acquire() as db:
      currequests=await db.fetchrow(f"SELECT * FROM requests WHERE user_id={ctx.author.id}")
      if len(currequests['ongoing'])==6:
        return await ctx.send("Sorry, you cannot request at this time. Please wait for your other requests to be completed and try again!")
      await ctx.author.send(f"Hello! You can currently request {6-len(currequests['ongoing'])} Pokemon! Which way would you like to request them?\n```A) Pokepaste\nB) Showdown Import\nC) PKx```\n\nJust say A, B, or C.")
      validmethods=['a','b','c']
      wait1=await self.bot.wait_for('message',check=lambda message: message.author==ctx.author and message.channel==ctx.author.dm_channel and message.content in validmethods)
      method=wait1.content.lower()
      if method=='a':
        await ctx.author.send("Okay, please send a Pokepaste link! Please ensure that this url starts with ``http://`` or ``https://``!")
        wait2=await self.bot.wait_for('message', check=lambda message: message.author==ctx.author and message.channel==ctx.author.dm_channel and urlparse(message.content).netloc=='pokepast.es')
        url=wait2.content
        async with aiohttp.ClientSession() as session:
          async with session.get(url+'/json') as resp:
            thing=await resp.read()
            print(thing)
            
        
        
def setup(bot):
  bot.add_cog(Requests(bot))
