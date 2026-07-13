# --- Serveur Flask pour UptimeRobot ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()


# --- Bot Discord ---
from datetime import datetime
import os
import asyncio
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1526002817058344960

en_jeu = {}
deco = {}

# 🔥 Désépingle tous les anciens messages sauf celui du statut
async def unpin_old_messages(channel, keep_id):
    pinned = await channel.pins()
    for msg in pinned:
        if msg.id != keep_id:
            try:
                await msg.unpin()
            except:
                pass


# 🔥 Toujours récupérer le message épinglé → jamais fetch_message
async def get_or_create_status_message():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("⚠️ Le bot ne voit pas le salon.")
        return None

    pinned = await channel.pins()

    # 🔥 Si un message est épinglé → c'est le message de statut
    if pinned:
        return pinned[0]

    # 🔥 Sinon on crée un nouveau message
    msg = await channel.send("📊 Statut des joueurs :\n\nChargement...")
    await asyncio.sleep(1)
    await msg.pin()

    # 🔥 Désépingle les anciens
    await unpin_old_messages(channel, msg.id)

    return msg


async def update_status():
    msg = await get_or_create_status_message()
    if msg is None:
        return

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

    # 🔥 S'assurer qu'il reste épinglé
    if not msg.pinned:
        await msg.pin()

    # 🔥 Désépingle les anciens
    await unpin_old_messages(msg.channel, msg.id)


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


@bot.command()
async def unpinall(ctx):
    channel = bot.get_channel(CHANNEL_ID)
    pinned = await channel.pins()
    count = 0

    for msg in pinned:
        try:
            await msg.unpin()
            count += 1
        except:
            pass

    await ctx.send(f"J'ai désépinglé {count} message(s).")


@bot.command()
async def resetstatus(ctx):
    channel = bot.get_channel(CHANNEL_ID)

    # 🔥 Supprimer tous les messages épinglés
    pinned = await channel.pins()
    for msg in pinned:
        try:
            await msg.delete()
        except:
            pass

    # 🔥 Nouveau message propre
    new_msg = await channel.send("📊 Statut des joueurs :\n\nAucun joueur enregistré.")
    await asyncio.sleep(1)
    await new_msg.pin()

    await ctx.send("Le message de statut a été réinitialisé.")


bot.run(os.getenv("TOKEN"))
