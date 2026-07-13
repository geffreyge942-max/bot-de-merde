from datetime import datetime
import os
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1526002817058344960
status_message_id = None

# 🔥 Juste des listes simples
en_jeu = set()
deco = set()

async def get_or_create_status_message():
    global status_message_id
    channel = bot.get_channel(CHANNEL_ID)

    if status_message_id is not None:
        try:
            msg = await channel.fetch_message(status_message_id)
            return msg
        except:
            pass

    msg = await channel.send("📊 Statut des joueurs :\n\nChargement...")
    status_message_id = msg.id
    return msg

async def update_status():
    msg = await get_or_create_status_message()

    texte = "**📊 Statut des joueurs :**\n\n"

    # 🔥 Joueurs en ligne
    for user in en_jeu:
        texte += f"🟢 **{user}** — en ligne\n"

    # 🔥 Joueurs hors ligne
    for user in deco:
        texte += f"🔴 **{user}** — hors ligne\n"

    await msg.edit(content=texte)

@bot.event
async def on_ready():
    print("Bot prêt !")
    await get_or_create_status_message()

@bot.command()
async def go(ctx):
    user = ctx.author.name

    # 🔥 Mise à jour des listes
    en_jeu.add(user)
    deco.discard(user)

    await update_status()
    await ctx.send(f"{user} est maintenant en ligne.")

@bot.command()
async def stop(ctx):
    user = ctx.author.name

    if user not in en_jeu:
        await ctx.send("Tu n'étais pas enregistré comme en ligne.")
        return

    en_jeu.discard(user)
    deco.add(user)

    await update_status()
    await ctx.send(f"{user} est maintenant hors ligne.")

# 🔥 Boucle anti-veille
async def anti_veille():
    while True:
        await asyncio.sleep(30)
        print("Anti-veille : toujours actif")

@bot.event
async def on_ready():
    print("Bot prêt !")
    await get_or_create_status_message()
    bot.loop.create_task(anti_veille())

bot.run(os.getenv("TOKEN"))
