import discord
from discord.ext import commands, tasks
import sqlite3
import random
import asyncio
import os

# ===================== CONFIG =====================
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
DATABASE = "tntlauncher.db"
# ==================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ----------------- Database setup -----------------
conn = sqlite3.connect(DATABASE)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0
)''')
conn.commit()

# ----------------- Bot events -----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    change_status.start()

# ----------------- Random presence/status -----------------
@tasks.loop(minutes=3)
async def change_status():
    activities = [
        "playing with TNT 💥",
        "testing TNTLauncher 🚀",
        "exploding servers 🔥",
        "watching the chaos 👀"
    ]
    await bot.change_presence(activity=discord.Game(name=random.choice(activities)))

# ----------------- Helper functions -----------------
def add_points(user_id, amount=1):
    c.execute("INSERT OR IGNORE INTO users (user_id, points) VALUES (?,0)", (user_id,))
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

def get_points(user_id):
    c.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    return result[0] if result else 0

def get_leaderboard(top=5):
    c.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT ?", (top,))
    return c.fetchall()

# ----------------- Commands -----------------
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def say(ctx, *, msg):
    await ctx.send(msg)

@bot.command()
async def tntdrop(ctx):
    """Random TNT event on a user"""
    members = [m for m in ctx.guild.members if not m.bot]
    if not members:
        return await ctx.send("No players found!")
    victim = random.choice(members)
    add_points(victim.id, random.randint(1,5))
    await ctx.send(f"💥 TNT dropped on {victim.mention}! They gained some points!")

@bot.command()
async def balance(ctx):
    pts = get_points(ctx.author.id)
    await ctx.send(f"{ctx.author.mention}, you have {pts} TNT points 💣")

@bot.command()
async def top(ctx):
    leaderboard = get_leaderboard()
    msg = "**🏆 TNTLauncher Leaderboard 🏆**\n"
    for i, (uid, pts) in enumerate(leaderboard, start=1):
        user = ctx.guild.get_member(uid)
        if user:
            msg += f"{i}. {user.display_name}: {pts} points\n"
    await ctx.send(msg)

@bot.command()
async def ignite(ctx, member: discord.Member):
    """Playful TNT ping"""
    add_points(member.id, 1)
    await ctx.send(f"💥 {member.mention} got ignited by {ctx.author.mention}!")

# ----------------- Random chat reactions -----------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # random 2% chance to react
    if random.random() < 0.02:
        await message.channel.send(random.choice(["💥", "🔥", "👀", "Boom!", "Kaboom!"]))
    await bot.process_commands(message)

# ----------------- Run bot -----------------
bot.run(TOKEN)

# ----------------- Commands/Features List -----------------
"""
TNTLauncher Bot Commands / Features:

1. !ping             → Bot replies "Pong!"
2. !say <message>    → Bot repeats your message
3. !tntdrop          → Random TNT event on a server member, gives points
4. !balance          → Shows your TNT points
5. !top              → Shows top 5 leaderboard
6. !ignite <member>  → Playful ping/explosion, gives points
7. Random status     → Changes every 3 minutes (themed messages)
8. Random reactions  → 2% chance to react to messages with 💥🔥👀
9. SQLite database   → Tracks points for each user persistently

Optional expansions:  
- Slash commands (/ping, /tntdrop)  
- More games/events for engagement  
- Auto announcements for new versions
"""


# bot.run("MTQ1NzMxMTE1Njc0OTMzNjgxMQ.GaJFAa.rTOzF3CLYHJjCZ1nKcMjTTuENsFEZWGvrj8NLY")

