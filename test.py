import discord
from discord.ext import commands
from discord import app_commands
import configparser
import datetime
import json
import os

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

TOKEN = config.get('Bot', 'TOKEN')
STATUS = config.get('Bot', 'STATUS')
EMBED_COLOR = int(config.get('Bot', 'EMBED_COLOR'), 16)
try:
    EMBED_COLOR = int(config.get('Bot', 'EMBED_COLOR'), 16)
except ValueError:
    print("Invalid EMBED_COLOR in config.ini. Using default")
    EMBED_COLOR = 0xFFFFFF
THUMBNAIL_URL = config.get('Bot', 'THUMBNAIL_URL')
FOOTER_TEXT = config.get('Bot', 'FOOTER_TEXT', fallback="DEFAULT")
REVIEW_CHANNEL_ID = int(config.get('Bot', 'REVIEW_CHANNEL_ID'))
ACCESS_ROLE_ID = int(config.get('Bot', 'ACCESS_ROLE_ID'))

VOUCHES_FILE = 'vouches.json'
if not os.path.exists(VOUCHES_FILE):
    with open(VOUCHES_FILE, 'w') as file:
        json.dump([], file)

intents = discord.Intents.default()
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = False  # Enable only if member-related events are required
bot = commands.Bot(command_prefix=".", intents=intents)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=STATUS))
    await bot.tree.sync()  
    print(f'init successful - {bot.user.name}')

@bot.tree.command(name="vouch", description="Submit a vouch with a review, star rating, and optional screenshot")
@app_commands.describe(product_name="Product you are reviewing", review_text="Review text here", stars="Rating (1-5)", screenshot="Optional")
@app_commands.choices(stars=[
    app_commands.Choice(name="⭐", value="1"),
    app_commands.Choice(name="⭐⭐", value="2"),
    app_commands.Choice(name="⭐⭐⭐", value="3"),
    app_commands.Choice(name="⭐⭐⭐⭐", value="4"),
    app_commands.Choice(name="⭐⭐⭐⭐⭐", value="5")
])
async def vouch(interaction: discord.Interaction, product_name: str, review_text: str, stars: app_commands.Choice[str], screenshot: discord.Attachment = None):
    start_count = int(stars.value)

    if start_count < 1 or start_count > 5:
        await interaction.response.send_message("Rate between 1 and 5.", ephemeral=True)
    start_count = int(stars.value) if stars and stars.value else 0

    vouches = []
    try:
        with open(VOUCHES_FILE, 'r') as file:
            vouches = json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading vouche file: {e}")
        vouches = []

    next_index = len(vouches) + 1

    vouch_data = {
        "index": next_index,
        "user_id": interaction.user.id,
        "avatar_url": str(interaction.user.avatar.url) if interaction.user.avatar else None,
        "avatar_url": str(interaction.user.avatar.url),
        "avatar_url": str(interaction.user.avatar.url) if interaction.user.avatar else None,
        "review_text": review_text,
        "stars": start_count,
        "screenshot_url": screenshot.url if screenshot else None,
        "timestamp": datetime.datetime.now().isoformat()
    }

    vouches.append(vouch_data)
    with open(VOUCHES_FILE, 'w') as file:
        json.dump(vouches, file, indent=4)

    embed = discord.Embed(
        title=f"#{next_index} Vouch Received",
        description=f"{interaction.user.mention} vouched!",
        color=EMBED_COLOR,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Product", value=product_name, inline=False)
    embed.add_field(name="Review", value=review_text, inline=False)
    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.set_thumbnail(url=interaction.user.avatar.url)
    if interaction.user.avatar:
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_image(url=screenshot.url)
    embed.set_footer(text=FOOTER_TEXT)

    review_channel = bot.get_channel(REVIEW_CHANNEL_ID)
    if review_channel:
        await review_channel.send(embed=embed)

    await interaction.response.send_message("Thanks", ephemeral=True)

@bot.tree.command(name="r", description="Recover and resend all prior vouches received")
async def r(interaction: discord.Interaction):
    if ACCESS_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("Access Denied.", ephemeral=True)
    if not interaction.user.roles or ACCESS_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("Access Denied.", ephemeral=True)
        return
    with open(VOUCHES_FILE, 'r') as file:
        vouches = json.load(file)

    if not vouches:
        await interaction.response.send_message("No vouches on file yet", ephemeral=True)
        return

    for vouch in vouches:
        timestamp = datetime.datetime.fromisoformat(vouch['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

        embed = discord.Embed(
            title=f"Vouch #{vouch['index']}",
            description=f"{vouch['username']} ({vouch['user_id']})",
            color=EMBED_COLOR,
            timestamp=datetime.datetime.fromisoformat(vouch['timestamp'])
        )
        embed.add_field(name="Product", value=vouch['product_name'], inline=False)
        embed.add_field(name="Review", value=vouch['review_text'], inline=False)
        embed.add_field(name="Stars", value="⭐" * int(vouch['stars']), inline=False)
        embed.add_field(name="Date and Time", value=timestamp, inline=False)
        embed.set_thumbnail(url=vouch['avatar_url'])
        if vouch['screenshot_url']:
            embed.set_image(url=vouch['screenshot_url'])
        embed.set_footer(text=FOOTER_TEXT)

        await interaction.channel.send(embed=embed)

    await interaction.followup.send("Restored.", ephemeral=True)

@bot.tree.command(name="s", description="Show vouch stats")
async def s(interaction: discord.Interaction):
    with open(VOUCHES_FILE, 'r') as file:
        vouches = json.load(file)

    total_reviews = len(vouches)
    now = datetime.datetime.now()

    reviews_last_30_days = 0
    reviews_last_7_days = 0
    reviews_last_1_day = 0
    reviews_last_1_hour = 0

    for vouch in vouches:
        time_diff = now - datetime.datetime.fromisoformat(vouch['timestamp'])
        if time_diff <= datetime.timedelta(days=30):
            reviews_last_30_days += 1
        if time_diff <= datetime.timedelta(days=7):
            reviews_last_7_days += 1
        if time_diff <= datetime.timedelta(days=1):
            reviews_last_1_day += 1
        if time_diff <= datetime.timedelta(hours=1):
            reviews_last_1_hour += 1

    embed = discord.Embed(
        title="Vouch Stats",
        color=EMBED_COLOR
    )

if not TOKEN or TOKEN.strip() == "":
    print("Error: Bot token is missing or invalid.")
else:
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Error: Invalid bot token provided.")
