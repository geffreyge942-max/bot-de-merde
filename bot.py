from datetime import datetime
import os
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Stockage des heures
en_jeu = {}
deco = {}

# ID du salon où afficher les infos
CHANNEL_ID = 1526002817058344960
status_message = None

async def update_status():
    global status_message

    channel = bot.get_channel(CHANNEL_ID)
    if status_message is None:
        status_message = await channel.send("Chargement des statuts...")

    texte = "**📊 Statut des joueurs :**\n\n"

    for user, start in en_jeu.items():
        diff = datetime.now() - start
        minutes = int(diff.total_seconds() // 60)
        texte += f"🟢 **{user}** — en jeu depuis **{minutes} min**\n"

    for user, stop_time in deco.items():
        diff = datetime.now() - stop_time
        minutes = int(diff.total_seconds() // 60)
        texte += f"🔴 **{user}** — déconnecté depuis **{minutes} min**\n"

    await status_message.edit(content=texte)

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
