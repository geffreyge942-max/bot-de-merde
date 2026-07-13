from datetime import datetime
import os
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1526002817058344960
status_message_id = None

en_jeu = {}
deco = {}

async def get_or_create_status_message():
    global status_message_id

    channel = bot.get_channel(CHANNEL_ID)

    # Si on a un ID, on essaie de récupérer le message
    if status_message_id is not None:
        try:
            msg = await channel.fetch_message(status_message_id)
            return msg
        except:
            pass  # Le message n'existe plus → on le recrée

    # Créer un nouveau message
    msg = await channel.send("📊 Statut des joueurs :\n\nChargement...")
    status_message_id = msg.id
    return msg

async def update_status():
    msg = await get_or_create_status_message()

    texte = "**📊 Statut des joueurs :**\n\n"

    for user, start in en_jeu.items():
        diff = datetime.now() - start
        minutes = int(diff.total_seconds() // 60)
        texte += f"🟢 **{user}** — en jeu depuis **{minutes} min**\n"

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
