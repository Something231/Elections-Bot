import os
import discord
from discord import app_commands, ui
from discord.ext import commands
from Keep_Alive import keep_alive
import json
import asyncio
import matplotlib.pyplot as plt

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)
candidate_id_to_name = {}


@bot.event
async def on_ready():
  game = discord.Game("Kaiser")
  await bot.change_presence(status=discord.Status.online, activity=game)
  print(f"Logged in as {bot.user}")
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)


class VotingDropdown(discord.ui.Select):

  def __init__(self, user_uwu):
    options = []
    for candidate_id in user_uwu:
      options.append(discord.SelectOption(label=candidate_id))
    super().__init__(placeholder="Who do you vote for?",
                     options=options,
                     min_values=1,
                     max_values=1)

  async def callback(self, interaction: discord.Interaction):
    user_id = interaction.user.id
    with open("hasvoted.json", 'r') as file:
      hasvotedls = json.load(file)
    if user_id in hasvotedls:
      return await interaction.response.send_message("You have already voted",
                                                     ephemeral=True)
    with open('votes.json', 'r') as file:
      votes = json.load(file)
    await interaction.response.send_message(f"You voted for {self.values[0]}!",
                                            ephemeral=True)
    candidate_id = str(self.values[0])
    if candidate_id not in votes:
      votes[candidate_id] = 0
    votes[candidate_id] += 1
    with open('votes.json', 'w') as file:
      json.dump(votes, file)
    hasvotedls.append(user_id)
    with open("hasvoted.json", 'w') as file:
      json.dump(hasvotedls, file)


class VotingView(discord.ui.View):

  def __init__(self, user_uwu):
    super().__init__()
    self.add_item(VotingDropdown(user_uwu))


class newparty(ui.Modal, title="Create Your Party!"):
  name = ui.TextInput(label="What is the name of your party?",
                      style=discord.TextStyle.short,
                      placeholder="One Nation Party",
                      required=True)
  description = ui.TextInput(
    label="Describe your party and some of its members.",
    style=discord.TextStyle.paragraph,
    max_length=40,
    required=True)

  async def on_submit(self, interaction: discord.Interaction):
    pname = str(self.name)
    desc = str(self.description)
    owner = str(interaction.user.id)
    with open('cand.json', 'r') as file:
      data = json.load(file)
    if pname in data:
      return await interaction.response.send_message(
        "You already have a party with that name!")
    data[pname] = {}
    data[pname]["desc"] = desc
    data[pname]['owner'] = owner
    with open('cand.json', 'w') as file:
      json.dump(data, file)
    embed = discord.Embed(
      title=self.title,
      description=
      f"**You have created the party {self.name} with the description {self.description}**",
      color=discord.Color.random())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="vote")
async def vote(interaction: discord.Interaction):
  with open("link.json", "r") as file:
    electstatus = json.load(file)
  if electstatus == ["running"]:
    user_id = interaction.user.id
    with open("hasvoted.json", 'r') as file:
      hasvotedls = json.load(file)
    if user_id in hasvotedls:
      return await interaction.response.send_message("You have already voted",
                                                     ephemeral=True)
    with open('cand.json', 'r') as file:
      user_owo = json.load(file)
    lisp = []
    for furry in user_owo.keys():
      lisp.append(furry)
    print("candidate_id_to_name:", candidate_id_to_name)
    await interaction.response.send_message("Click the dropdown to vote",
                                            view=VotingView(lisp),
                                            ephemeral=True)
  else:
    await interaction.response.send_message("The election is not running!")


@bot.tree.command(name="create-party")
async def create_party(interaction: discord.Interaction):
  with open("link.json", "r") as file:
    electstatus = json.load(file)
  print(electstatus)
  if electstatus != ["config"]:
    return await interaction.response.send_message(
      "You can only create a party when an election is upcoming",
      ephemeral=True)
  return await interaction.response.send_modal(newparty())


@bot.tree.command(name="coalition")
async def coalition(interaction: discord.Interaction):
  with open("link.json", "r") as file:
    electstatus = json.load(file)
  if electstatus != ["config"]:
    return await interaction.response.send_message(
      "You can only create coalititions before the election starts.",
      ephemeral=True)
  with open("cand.json", "r") as file:
    cand = json.load(file)
  user_id = interaction.user.id
  for item in cand.keys():
    if cand[item]['owner'] == "e":
      pass
  with open("coalitions.json", "r") as file:
    coalitions = json.load(file)


@bot.command()
async def sniff(ctx):
  await ctx.send("snoff")


@bot.command()
async def uwu(ctx):
  for i in range(3):
    await ctx.send("owo")


@bot.command()
async def poll(ctx, *, question):
  options = question.split("|")
  question = options[0]
  del options[0]
  if len(options) <= 1:
    await ctx.send('You need more than one option to make a poll!')
    return
  if len(options) > 10:
    await ctx.send('You cannot make a poll for more than 10 things!')
    return
  if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
    reactions = ['👍', '👎']
  else:
    reactions = [
      '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'
    ]
  description = []
  for i, option in enumerate(options):
    description += '\n {} {}'.format(reactions[i], option)
  embed = discord.Embed(title=question, description=''.join(description))
  react_message = await ctx.send(embed=embed)
  for reaction in reactions[:len(options)]:
    await react_message.add_reaction(reaction)
  await ctx.message.delete()


@commands.is_owner()
@bot.command()
async def config_election(ctx):
  g = ["config"]
  t = {}
  with open("cand.json", 'w') as f:
    json.dump(t, f)
  with open("link.json", 'w') as f:
    json.dump(g, f)
  em = discord.Embed(
    title="Run for Server Admin",
    description=
    "Are you interested in becoming the admin for the server?             Just use the ***/create-party*** command!",
    color=discord.Color.green()  # You can set a color for the embed
  )
  return await ctx.send(embed=em)


@commands.is_owner()
@bot.command()
async def start_election(ctx):
  try:
    with open('link.json', 'r') as file:
      electstatus = json.load(file)
    if electstatus != ["config"]:
      return await ctx.send("Election has not been configured yet!")
    electstatus = ['running']
    with open('link.json', 'w') as file:
      json.dump(electstatus, file)

    clear = []
    with open('hasvoted.json', 'w') as file:
      json.dump(clear, file)

    votes = {}
    with open("votes.json", 'w') as file:
      json.dump(votes, file)

    with open("coalitions.json", "w") as file:
      json.dump(votes, file)

    with open('cand.json', 'r') as file:
      user_uwu = json.load(file)
    em = discord.Embed(title="Vote for the Server Admin",
                       color=discord.Color.blue(),
                       description="Vote by using /vote")
    for party in user_uwu:
      em.add_field(name=f"***{party}***", value="Party")
      return await ctx.send(embed=em)
  except Exception as e:
    await ctx.send(f"An error occurred: {e}")


#eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
@commands.is_owner()
@bot.command()
async def eval_election(ctx):
  with open("votes.json", 'r') as file:
    votes = json.load(file)
  em = discord.Embed(title="Election Results",
                     color=discord.Color.orange(),
                     description="The results are displayed below")
  maxvotes = 0
  maxparty = "null"
  for party in votes.keys():
    vote_count = votes[party]
    if vote_count > maxvotes:
      maxvotes = vote_count
      maxparty = party
    em.add_field(name=party, value=f"Votes: {vote_count}", inline=False)
  em.add_field(name=f"That means the winning party is {maxparty}",
               value="The chancellor role has been applied")
  #with open("chancellor.json", 'r') as file:
  #prevchancellor = json.load(file)
  #role = discord.utils.get(ctx.guild.roles, name="Chancellor")
  #if prevchancellor:
  #  anime = int(prevchancellor)
  #  member = ctx.guild.get_member(anime)
  #  await member.remove_roles(role)
  #user_id = int(maxkey)
  #member = ctx.guild.get_member(user_id)
  #await member.add_roles(role)
  #prevchancellor = user_id
  #with open("chancellor.json", "w") as file:
  #  json.dump(prevchancellor, file)

  electstatus = ["over"]
  with open("link.json", 'w') as file:
    json.dump(electstatus, file)
  await ctx.send(embed=em)


@bot.command()
async def current_results(ctx):
  with open("votes.json", 'r') as file:
    votes = json.load(file)
  x = []
  y = []
  for candidate in votes.keys():
    vote_count = votes[candidate]
    x.append(candidate)
    y.append(vote_count)
  plt.bar(x, y, color='Orange')
  plt.xlabel('Candidates')
  plt.ylabel('Votes')
  plt.title('Election Results (Current)')
  plt.savefig('graph.png')
  await ctx.send(file=discord.File('graph.png'))


@bot.event
async def on_message(message):
  if any(word in message.content.lower() for word in ["kys"]):
    channel = message.channel
    await channel.send(file=discord.File('kys-keep-yourself-safe.gif'))
  await bot.process_commands(message)


keep_alive()
bot.run(os.getenv('TOKEN'))
