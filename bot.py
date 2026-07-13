from datetime import datetime
import os
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1526002817058344960
en_jeu = {}
deco = {}

async def get_or_create_status_message():
    channel = bot.get_channel(CHANNEL_ID)

    # 🔥 Toujours récupérer le message épinglé → fiable à 100%
    pinned = await channel.pins()
    if pinned:
        return pinned[0]

    # 🔥 Sinon on crée un seul message
    msg = await channel.send("📊 Statut des joueurs :\n\nChargement...")
    await msg.pin()
    return msg

async def update_status():
    msg = await get_or_create_status_message()

    texte = "**📊 Statut des joueurs :**\n\n"

    # Joueurs en jeu
    for user, start in en_jeu.items():
        diff = datetime.now() - start
        minutes = int(diff.total_seconds() // 60)
        texte += f"🟢 **{user}** — en jeu depuis **{minutes} min**\n"

    # Joueurs déconnectés
    for user, stop_time in deco.items():
        diff = datetime.now() - stop_time
        minutes = int(diff.total_seconds() // 60)
        texte += f"🔴 **{user}** — déconnecté depuis **{minutes} min**\n"

    await msg.edit(content=texte)

@bot.event
async def on_ready():
    print("Bot prêt !")
    await get_or_create_status_message()

@bot.command()
async def go(ctx):
    user = ctx.author.name
    en_jeu[user] = datetime.now()
    deco.pop(user, None)
    await update_status()
    await ctx.send(f"{user} vient de lancer le jeu.")

@bot.command()
async def stop(ctx):
    user = ctx.author.name
    if user not in en_jeu:
        await ctx.send("Tu n'étais pas enregistré comme en jeu.")
        return

    deco[user] = datetime.now()
    en_jeu.pop(user, None)
    await update_status()
    await ctx.send(f"{user} vient de se déconnecter.")

bot.run(os.getenv("TOKEN"))
