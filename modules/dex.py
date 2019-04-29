import discord, requests, json
from discord.ext import commands, flags

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
      if gen in entries.keys():
        return entries[gen]
  
  def isHidden(self,abilities):
    ab={}
    for ability in abilities:
      if 'hidden' in ability.keys():
        ab[ability['name']]=True
      else:
        ab[ability['name']]=False
    return ab
  
  def ratios(self,genders):
    gender={}
    if 'male' in genders.keys():
      gender['male']=True
    else:
      gender['male']=False
    if 'female' in genders.keys():
      gender['female']=True
    else:
      gender['female']=False
    return gender
  
  @commands.command(name="dex")
  async def dex(self,ctx,*pokemon, flag: flags.FlagParser(
    shiny=bool,
    form=str,
    mega=bool,
    x=bool,
    y=bool
  ) = flags.EmptyFlags):
    shiny=flag['shiny']
    mega=flag['mega']
    x=flag['x']
    y=flag['y']
    pkmn='_'.join(pokemon)
    pkmngif='-'.join(pokemon)
    pokedex=requests.get(f"https://raw.githubusercontent.com/jalyna/oakdex-pokedex/master/data/pokemon/{pkmn.lower()}.json")
    jsona=pokedex.json()
    if not jsona:
      return await ctx.send("Pokemon not found.")
    entries=jsona['pokedex_entries']
    en=self.latestGen(entries)
    entry=en['en']
    abilities=""
    stats=""
    steps=f"{str(jsona['hatch_time'][0])} to {str(jsona['hatch_time'][1])} steps"
    national=jsona['national_id']
    ratios=""
    height=None
    weight=None
    if jsona['gender_ratios']:
      gender=self.ratios(jsona['gender_ratios'])
      if gender['male']==True:
        ratios+=f"Male - {jsona['gender_ratios']['male']}%\n"
      else:
        ratios+=f"Male - 0%\n"
      if gender['female']==True:
        ratios+=f"Female - {jsona['gender_ratios']['female']}%"
      else:
        ratios+=f"Female - 0%"
    else:
      ratios="No Genders"
    evolution_from="Nothing"
    if jsona['evolution_from']:
      evolution_from=jsona['evolution_from']
    category=jsona['categories']['en']
    colour=jsona['color']
    name=jsona['names']['en']
    catch_rate=jsona['catch_rate']
    egg_groups=', '.join(jsona['egg_groups'])
    exp=jsona['base_exp_yield']
    category=jsona['categories']['en']
    yields=""
    stat_names={
      "hp": "HP",
      "atk": "Attack",
      "def": "Defense",
      "sp_atk": "Special Attack",
      "sp_def": "Special Defense",
      "speed": "Speed"
      }
    types=None
    for k,v in jsona['ev_yield'].items():
      yields+=f"{stat_names[k]} - {v}\n"
    #if mega is not true
    if mega==False and x==False and y==False:
      hid={True: '[Hidden]', False: ''}
      ab=self.isHidden(jsona['abilities'])
      for k,v in ab.items():
        abilities+=f"{k} {hid[v]}\n"
      for k,v in jsona['base_stats'].items():
        stats+=f"{stat_names[k]} - {v}\n"
      types=', '.join(jsona['types'])
      height=jsona['height_us']
      weight=jsona['weight_us']
    
    #if mega is true
    if x==True or y==True:
      mega=True
    if mega==True:
      if x==False and y==False:
        abilities=jsona['mega_evolutions'][0]['ability']
        types=', '.join(jsona['mega_evolutions'][0]['types'])
        height=jsona['mega_evolutions'][0]['height_us']
        weight=jsona['mega_evolutions'][0]['weight_us']
        for k,v in jsona['mega_evolutions'][0]['base_stats'].items():
          stats+=f"{stat_names[k]} - {v}\n"
      if x==True:
        jsonb=None
        for i in jsona['mega_evolutions']:
          if i['image_suffix']=='megax':
            jsonb=i
        abilities=jsonb['ability']
        types=', '.join(jsonb['types'])
        height=jsonb['height_us']
        weight=jsonb['weight_us']
        for k,v in jsonb['base_stats'].items():
          stats+=f"{stat_names[k]} - {v}\n"
      if y==True:
        jsonb=None
        for i in jsona['mega_evolutions']:
          if i['image_suffix']=='megay':
            jsonb=i
        abilities=jsonb['ability']
        types=', '.join(jsonb['types'])
        height=jsonb['height_us']
        weight=jsonb['weight_us']
        for k,v in jsonb['base_stats'].items():
          stats+=f"{stat_names[k]} - {v}\n"
    evolutions="None"
    if jsona['evolutions']:
      evolutions=""
      for i in jsona['evolutions']:
        if 'item' in i.keys():
          if 'conditions' in i.keys():
            evolutions+=f"{i['to']} by using a(n) {i['item']} | Conditions: {', '.join(i['conditions'])}\n"
          else:
            evolutions+=f"{i['to']} by using a(n) {i['item']}\n"
        if 'level' in i.keys():
          if 'conditions' in i.keys():
            evolutions+=f"{i['to']} by leveling to level {i['level']} | Conditions: {', '.join(i['conditions'])}\n"
          else:
            evolutions+=f"{i['to']} by leveling to level {i['level']}\n"
        if 'level_up' in i.keys() and 'conditions' in i.keys():
          evolutions+=f"{i['to']} upon leveling with the following conditions met: {', '.join(i['conditions'])}\n"
        if 'happiness' in i.keys():
          if 'conditions' in i.keys():
            evolutions+=f"{i['to']} upon leveling at max happiness | Conditions: {', '.join(i['conditions'])}\n"
          else:
            evolutions+=f"{i['to']} upon leveling at max happiness\n"
        if 'trade' in i.keys():
          if 'hold_item' in i.keys():
            evolutions+=f"{i['to']} when traded while holding a(n) {i['hold_item']}\n"
          else:
            evolutions+=f"{i['to']} when traded\n"
        if 'hold_item' in i.keys() and 'trade' not in i.keys():
          if 'conditions' in i.keys():
            evolutions+=f"{i['to']} upon leveling while holding a(n) {i['hold_item']} | Conditions: {', '.join(i['conditions'])}\n"
          else:
            evolutions+=f"{i['to']} upon leveling while holding a(n) {i['hold_item']}\n"
        if 'move_learned' in i.keys():
          if 'conditions' in i.keys():
            evolutions+=f"{i['to']} upon leveling after learning {i['move_learned']} | Conditions: {', '.join(i['conditions'])}\n"
          else:
            evolutions+=f"{i['to']} upon leveling after learning {i['move_learned']}\n"
        if 'conditions' in i.keys() and 'item' not in i.keys() and 'level' not in i.keys() and 'level_up' not in i.keys() and 'happiness' not in i.keys() and 'hold_item' not in i.keys() and 'move_learned' not in i.keys():
          evolutions+=f"{i['to']} upon meeting the following conditions: {', '.join(i['conditions'])}\n"
    optiongif=''
    if shiny==True:
      optiongif='-shiny'
    m=''
    if mega==True:
      m='-mega'
    thumbnail=f"https://play.pokemonshowdown.com/sprites/xyani{optiongif}/{pkmngif.lower()}{m}.gif"
    description=f"""
Abilities: 
{abilities}

Height: {height}

Weight: {weight}

Base Stats: 
{stats}

Base Yields: 
{yields}

Gives {exp} EXP upon defeat (base value)

Gender Ratios: 
{ratios}

Steps To Hatch: {steps}

Egg Groups: 
{egg_groups}

Evolutions:
{evolutions}

Evolves From: {evolution_from}


{entry}
    """
    embed=discord.Embed(description=description,colour=discord.Colour(value=colours[colour]))
    embed.set_image(url=thumbnail)
    embed.set_footer(text=f"{name}, The {category}")
    await ctx.send(embed=embed)
    
def setup(bot):
  bot.add_cog(Dex(bot))
