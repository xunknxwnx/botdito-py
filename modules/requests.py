import discord, aiohttp, json
from discord.ext import commands
from urllib.parse import urlparse
from ast import literal_eval
from goto import with_goto

class Requests(commands.Cog, name='Requests'):
  def __init__(self,bot):
    self.bot=bot
    
  def chunk(self,l,size):
    for i in range(0,len(l),size):
      yield l[i:i+size]
   
  def pokemon_getter(self,team,string):
    thing=team.split(string)
    pokemon=[]
    for i in thing:
      pokemon.append(i)
    return pokemon
    
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
    role=discord.utils.get(ctx.guild.roles,name='SnowBuddy')
    if role not in ctx.author.roles:
      await ctx.author.add_roles(role)
    
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
      final=list(self.chunk(people, 25))
      await ctx.send(final)
      text=""
      index=1
      for i in final:
        text+=f"{index} - {i.name}\n"
        index+=1
      embed=discord.Embed(description=text, colour=discord.Colour.blue())
      await ctx.send("Please select a user by saying a number.",embed=embed)
      def check(m):
        return True if m.author==ctx.author and m.channel==ctx.channel else False
      wait=await self.bot.wait_for('message', check=check)
      num=int(wait.content)
      await ctx.send(list(final)[num-1])
      await self.bot.db.release(db)
      
  @commands.group(name='request')
  @with_goto
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
      label .start
      wait1=await self.bot.wait_for('message',check=lambda message: message.author==ctx.author and message.channel==ctx.author.dm_channel and message.content in validmethods)
      method=wait1.content.lower()
      if method=='a':
        await ctx.author.send("Okay, please send a Pokepaste link! Please ensure that this url starts with ``http://`` or ``https://``!")
        label .teampkps
        wait2=await self.bot.wait_for('message', check=lambda message: message.author==ctx.author and message.channel==ctx.author.dm_channel and urlparse(message.content).netloc=='pokepast.es')
        url=wait2.content
        async with aiohttp.ClientSession() as session:
          async with session.get(url+'/json') as resp:
            thing=await resp.read()
            thing=literal_eval(thing.decode('utf-8'))
            team=self.pokemon_getter(thing['paste'],'\r\n\r\n')
            team2='\n'.join(team).replace('\r\n','\n')
            for i in team:
              i.replace('\r\n','\n')
            await ctx.author.send(f"Is this team correct?\n```{team2}```")
            wait3=await self.bot.wait_for('message', check=lambda message: message.author==ctx.author and message.channel==ctx.author.dm_channel and message.content.lower() in ['yes','no'])
            answer=wait3.content.lower()
            if answer=='no':
              await ctx.author.send("Okay, please resubmit the url!")
              goto .teampkps
            else:
              channel=discord.utils.get(ctx.guild.channels,name='genning-requests')
              await ctx.author.send("What is your in game name? This is so the genners can find you quickly and easy.")
              wait4=await self.bot.wait_for('message', check=lambda message: message.author==ctx.author and message.channel==ctx.author.dm_channel)
              ign=wait4.content
              haha='\n'
              msg=await channel.send(f"{ign} ({ctx.author.mention}) has submitted the following team!\n```{team2}```")
              for i in team:
                await db.execute(f"UPDATE requests SET requests=requests || ARRAY ['{i}'],ongoing=ongoing || ARRAY['{i}'] WHERE user_id={ctx.author.id}")
              await db.execute(f"INSERT INTO ongoing(message, status, team, requester) VALUES({msg.id}, 'NOT DONE', '{team2}', {ctx.author.id})")
            session.close()
      elif method=='b':
        await ctx.author.send("Okay! Please send a valid Pokemon Showdown team.")
        wait2=await self.bot.wait_for('message', check=lambda message: message.author==ctx.author and message.channel==ctx.author.dm_channel)
        team=wait2.content
        team=self.pokemon_getter(team,'\n\n')
        channel=discord.utils.get(ctx.guild.channels,name='genning-requests')
        await ctx.author.send("What is your in game name? This is so the genners can find you quickly and easy.")
        wait3=await self.bot.wait_for('message', check=lambda message: message.author==ctx.author and message.channel==ctx.author.dm_channel)
        ign=wait3.content
        haha='\n'
        msg=await channel.send(f"{ign} ({ctx.author.mention}) has submitted the following team!\n```{haha.join(team)}```")
        for i in team:
          await db.execute(f"UPDATE requests SET requests=requests || ARRAY ['{i}'],ongoing=ongoing || ARRAY['{i}'] WHERE user_id={ctx.author.id}")
        await db.execute(f"INSERT INTO ongoing(message, status, team, requester) VALUES({msg.id}, 'NOT DONE', '{haha.join(team)}', {ctx.author.id})")
      elif method=='c':
        return await ctx.author.send("NOT SUPPORTED YET")
      await self.db.release(db)
                               
  @commands.command(name='myreqs', aliases=['myrequests','reqs']]
  async def myreqs(self,ctx, number:int=None):
    async with self.bot.db.acquire() as db:
      reqs=await db.fetch(f"SELECT * FROM ongoing WHERE requester={ctx.author.id}")
      if not reqs:
        return await ctx.send("You have no requests!")
      return await ctx.send("Not currently ready!")

def setup(bot):
  bot.add_cog(Requests(bot))
