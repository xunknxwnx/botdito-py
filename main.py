import discord, asyncio, random, os, asyncpg, include, time
from discord.ext import commands
from datetime import datetime

config=include.path('/root/botdito-py/config/config.py')

class Snowbuddy(commands.Bot):
  def __init__(self):
    super().__init__(command_prefix=config.command_prefix)
    self.config = config
    self.startup_extensions = ['jishaku',
                               'modules.requests',
                               'modules.dex',
                               'modules.others',
                               'modules.fun',
                               'modules.events',
                               'modules.admin'
                              ]
    self.path = os.path.dirname(os.path.realpath(__file__))
 
  async def start_db(self):
    self.db=await asyncpg.create_pool(dsn=config.dsn)

  async def on_ready(self):
    try:
      await self.start_db()
      print('db loaded')
    except:
      print('ok it didnt load')
    self.loop.create_task(self.presence())
  
  async def presence(self):
    while not self.is_closed():
      await self.change_presence(
        activity=discord.Game(
          name=random.choice(
            (
              "Pokemon Let's Go Pikachu!",
              "Pokemon Let's Go Eevee!",
              "Pokemon Sword",
              "Pokemon Shield"
            )
          ),
        ),
      )
      await asyncio.sleep(45)
      
  def run(self):
    loaded=0
    for extension in self.startup_extensions:
      try:
        self.load_extension(extension)
        loaded +=1
      except Exception as er:
        print(er)
      print(f"Loaded {loaded} cogs")
      
      
    super().run(self.config.token,reconnect=True)
        
if __name__ == "__main__":
  Snowbuddy().run()
