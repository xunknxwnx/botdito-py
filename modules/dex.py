import discord, requests, json
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
  
  def isHidden(self,abilities):
    ab={}
    for ability in abilities:
      if 'hidden' in ability.keys():
        ab[ability['name']]['hidden']=True
      else:
        ab[ability['name']]['hidden']=False
    return hidden, nothid
  
  @commands.command(name="dex")
  async def dex(self,ctx,*pokemon):
    pkmnfile='_'.join(pokemon)
    pokedex=requests.get(f"https://raw.githubusercontent.com/jalyna/oakdex-pokedex/master/data/pokemon/{pkmnfile.lower()}.json")
    jsona=pokedex.json()
    if not jsona:
      return await ctx.send("Pokemon not found.")
    entries=jsona['pokedex_entries']
    en=self.latestGen(entries)
    entry=en['en']
    category=jsona['categories']['en']
    abilities=""
    hid={True: '[Hidden]', False: ''}
    ab=self.isHidden(jsona['abilities'])
    for k,v in ab.items():
      await ctx.send(f"{k} - {v}")
    stats=""
    yields=""
    stat_names={
      "hp": "HP",
      "atk": "Attack",
      "def": "Defense",
      "sp_atk": "Special Attack",
      "sp_def": "Special Defense",
      "speed": "Speed"
    }
    for k,v in jsona['base_stats'].items():
      stats+=f"{stat_names[k]} - {v}\n"
    for k,v in jsona['ev_yield'].items():
      yields+=f"{stat_names[k]} - {v}\n"
    catch_rate=jsona['catch_rate']
    egg_groups=', '.join(jsona['egg_groups'])
    name=jsona['names']['en']
    category=jsona['categories']['en']
    colour=jsona['color']
    types=', '.join(jsona['types'])
    height=jsona['height_us']
    weight=jsona['weight_us']
    steps=' to '.join(jsona['hatch_time'])
    national=jsona['national_id']
    dictionary=json.loads(jsona['gender_ratios'])
    await ctx.send(dictionary)
    
def setup(bot):
  bot.add_cog(Dex(bot))
