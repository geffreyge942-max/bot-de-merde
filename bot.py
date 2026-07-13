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


# --- Ton bot Discord ---
from datetime import datetime
import os
import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1526232996175413280
status_message_id = None

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


async def get_or_create_status_message():
    global status_message_id

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("⚠️ Le bot ne voit pas le salon. Vérifie l'ID.")
        return None

    # Si un message existe déjà, on tente de le récupérer
    if status_message_id is not None:
        try:
            msg = await channel.fetch_message(status_message_id)

            # 🔥 On s'assure qu'il est épinglé
            if not msg.pinned:
                await msg.pin()

            # 🔥 On désépingle les anciens
            await unpin_old_messages(channel, msg.id)

            return msg
        except:
            pass

    # Sinon on crée un nouveau message
    msg = await channel.send("📊 Statut des joueurs :\n\nChargement...")
    status_message_id = msg.id

    # 🔥 On épingle le nouveau message
    await msg.pin()

    # 🔥 On désépingle les anciens
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

    # 🔥 On s'assure qu'il reste épinglé
    if not msg.pinned:
        await msg.pin()

    # 🔥 On désépingle les anciens
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


# 🔥 Commande pour désépingler TOUT (sauf le message de statut)
@bot.command()
async def unpinall(ctx):
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        await ctx.send("Impossible de trouver le salon.")
        return

    pinned = await channel.pins()
    count = 0

    for msg in pinned:
        if msg.id != status_message_id:
            try:
                await msg.unpin()
                count += 1
            except:
                pass

    await ctx.send(f"J'ai désépinglé **{count}** message(s).")


bot.run(os.getenv("TOKEN"))
