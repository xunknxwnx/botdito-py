import discord, requests
from discord.ext import commands

colours={
  'Red': 16724530,
  'Blue': 2456831,
  'Yellow': 16773977,
  'Green': 4128590,
  'Black': 3289650,
  'Brown': 10702874,
  'Purple': 10894824,
  'Gray': 9868950,
  'White': 14803425,
  'Pink': 16737701
}

class Dex(commands.Cog, name="Dex"):
  def __init__(self,bot):
    self.bot = bot
    
  @commands.command(name="dex")
  async def dex(self,ctx,*pokemon):
    pkmnfile='_'.join(pokemon)
    pokedex=requests.get(f"https://github.com/jalyna/oakdex-pokedex/blob/master/data/pokemon/{pkmnfile}.json")
    json=pokedex.json()
    print(json)
    
def setup(bot):
  bot.add_cog(Dex(bot))
