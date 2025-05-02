import discord
from config import *
from babel.dates import format_datetime
from datetime import datetime

async def send_error(channel):
	embed = discord.Embed(title="Erreur.", description="Erreur interne, demandez de l'aide à un membre du staff ou à <@598076783186935808>.", color=discord.Color.red())
	embed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url=BOT_ICON)
	await channel.send(embed=embed)
	return

async def handle_command(command, user, username, user_pfp, staff_request, channel, bot, logger):
    if command in ["start"]:
        await handle_start(user, username, user_pfp, staff_request, channel, bot, logger)

    elif command in ["stop"]:
        await handle_stop(user, username, user_pfp, staff_request, channel, bot, logger)

    elif command in ["maintenance"]:
        await handle_maintenance(user, username, user_pfp, staff_request, channel, bot, logger)

    elif command in ["post"]:
        await handle_post(user, username, user_pfp, staff_request, channel, bot, logger)


async def handle_start(user, username, user_pfp, staff_request, channel, bot, logger):
    if not (Gerant in staff_request):
        await send_permission_error(username, user_pfp, channel)
        return

    try:
        channel = bot.get_channel(channelBot)
        await channel.send(f"-# <@&{ping_annonces_bot}>")
        embed = discord.Embed(description=f"## {emoji_error}  {nom_bot} part temporairement !", color=discord.Color.red())
        embed.add_field(name="\n🛠 Statut", value="Hors ligne", inline=True)
        embed.set_footer(text=f"{nom_bot} | {get_now()}", icon_url=BOT_ICON)
        await channel.send(embed=embed)

        logger.info("Début de la maintenance.")
        await bot.get_channel(log_channel).send("Message posté")

    except Exception as e:
        logger.info(e)
        await send_error(channel)


async def handle_stop(user, username, user_pfp, staff_request, channel, bot, logger):
    if not (Gerant in staff_request):
        await send_permission_error(username, user_pfp, channel)
        return

    try:
        channel = bot.get_channel(channelBot)
        await channel.send(f"-# <@&{ping_annonces_bot}>")
        embed = discord.Embed(description=f"## 🎉 {nom_bot} est de retour !\n *(avec le site web)*", color=discord.Color.green())
        embed.add_field(name="\n🛠 Statut", value="En ligne", inline=True)
        embed.set_footer(text=f"{nom_bot} | {get_now()}", icon_url=BOT_ICON)
        await channel.send(embed=embed)

        logger.info("Fin de la maintenance.")
        await bot.get_channel(log_channel).send("Message posté")

    except Exception as e:
        logger.info(e)
        await send_error(channel)


def get_now():
    return format_datetime(datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')


async def send_permission_error(username, user_pfp, channel):
    embed = discord.Embed(description=f"🔒 Nécessite le rôle {Gerant}", color=discord.Color.red())
    embed.set_author(name=username, icon_url=user_pfp)
    embed.set_footer(text=f"{nom_bot} | {get_now()}", icon_url=BOT_ICON)
    await channel.send(embed=embed)
