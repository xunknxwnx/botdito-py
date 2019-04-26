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
games=[
  "Red",
  "Blue",
  "Yellow",
  "Gold",
  "Silver",
  "Crystal",
  "Ruby",
  "Sapphire",
  "Emerald",
  "FireRed",
  "LeafGreen",
  "Diamond",
  "Pearl",
  "Platinum",
  "HeartGold",
  "SoulSilver",
  "Black",
  "White",
  "Black 2",
  "White 2", 
  "X",
  "Y",
  "Omega Ruby",
  "Alpha Sapphire",
  "Sun",
  "Moon",
  "Ultra Sun",
  "Ultra Moon"
]

class Dex(commands.Cog, name="Dex"):
  def __init__(self,bot):
    self.bot = bot
    
  def latestGen(self,entries):
    for gen in games:
      if entries[gen]:
        return entries[gen]
    
  @commands.command(name="dex")
  async def dex(self,ctx,*pokemon):
    pkmnfile='_'.join(pokemon)
    print(pkmnfile)
    pokedex=requests.get(f"https://raw.githubusercontent.com/jalyna/oakdex-pokedex/master/data/pokemon/{pkmnfile.lower()}.json")
    json=pokedex.json()
    if not json:
      return await ctx.send("Pokemon not found.")
    entries=json['pokedex_entries']
    en=self.latestGen(entries)
    entry=en['en']
    category=json['categories']['en']
    abilities=""
    hid={True: '[Hidden]', False: ''}
    for i in json['abilities']:
      abilities+=f"{i.name} {hid[i.hidden]}\n"
    
    
def setup(bot):
  bot.add_cog(Dex(bot))
