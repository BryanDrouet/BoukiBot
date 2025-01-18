import discord, json, locale, database, datetime, requests
from discord.ext.commands import Bot
from babel.dates import format_datetime


APPLICATION_ID = "IdBot"
token = "Token"
emoji_worked = "✅"
emoji_error = "❌"  #Officiel
channelBot = IdChannel
log_channel = IdChannel
BOT_PREFIX = "+"
nom_bot = "BotPersonnalisé"
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
discord_error_rgb_code = discord.Color.from_rgb(239, 83, 80)
intents = discord.Intents.all()
bot = Bot(command_prefix=BOT_PREFIX, intents=intents)
db_handler = database.pythonboat_database_handler(bot)


def currency_symbol(self, test=False, value="unset"):
	self.currency_symbol = "🪙"

async def transfer_money_to_vendor(vendeur_id, amount):
	try:
		# Charger le fichier JSON des utilisateurs
		with open("users.json", "r") as f:
			users_data = json.load(f)

		# Vérifier si l'utilisateur existe
		if str(vendeur_id) in users_data:
			vendeur_balance = users_data[str(vendeur_id)]["cash"]  # Récupérer le solde en cash
			new_balance = vendeur_balance + amount  # Calculer le nouveau solde
			users_data[str(vendeur_id)]["cash"] = new_balance  # Mettre à jour le solde du vendeur

			# Sauvegarder les données mises à jour
			with open("users.json", "w") as f:
				json.dump(users_data, f, indent=4)
			print(f"Montant de {amount} ajouté au vendeur {vendeur_id}. Nouveau solde: {new_balance}")
		else:
			print(f"Utilisateur {vendeur_id} non trouvé dans les données.")
	
	except Exception as e:
		print(f"Erreur lors du transfert d'argent au vendeur: {e}")

async def get_user_input(message, default_spell=True):
	print("En attente de la réponse de l'utilisateur.")
	answer = await bot.wait_for("message", check=lambda response: response.author == message.author and response.channel == message.channel)
	answer = answer.content
	if default_spell:
		answer = answer.lower().strip()

	return answer

async def get_user_id(param):
	reception_user_beta = str(param[1])  # the mention in channel gives us <@!USERID> OR <@USERIRD>
	reception_user = ""
	for i in range(len(reception_user_beta)):
		try:
			reception_user += str(int(reception_user_beta[i]))
		except:
			pass
	return reception_user

async def get_role_id_multiple(user_input):
	roles = user_input.split(" ")  # so we get a list
	roles_clean = []

	for i in range(len(roles)):
		current_role = roles[i]
		new_current_role = ""
		for i in range(len(current_role)):
			try:
				new_current_role += str(int(current_role[i]))
			except:
				pass
		roles_clean.append(new_current_role)
	return roles_clean

async def get_role_id_single(parameter):
	role_beta = str(parameter)  # see another instance where i use this to see why
	role_clean = ""
	for i in range(len(role_beta)):
		try:
			role_clean += str(int(role_beta[i]))
		except:
			pass
	return role_clean

async def send_embed(title, description, channel, color="default"):
	# some default colors
	colors = [0xe03ca5, 0xdd7b28, 0x60c842, 0x8ae1c2, 0x008c5a, 0xc5bcc5]
	if color == "default": color = 0xe03ca5
	# create the embed
	embed = discord.Embed(title=title, description=description, color=color)
	await channel.send(embed=embed)
	return


async def send_error(channel):
	current_time = format_datetime(
		datetime.datetime.now(),
		format="d MMMM y 'à' HH:mm",
		locale="fr_FR"
	)
	embed = discord.Embed(title="Erreur.", description="Erreur interne, demandez de l'aide à un membre du staff ou à @Bryan_Drouet.", color=0xff0000)
	embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
	await channel.send(embed=embed)
	return

async def log_transaction(user, channel_id, change_type, amount, reason, before_balance, after_balance):
		current_time = format_datetime(
			datetime.datetime.now(),
			format="d MMMM y 'à' HH:mm",
			locale="fr_FR"
		)
		log_channel = bot.get_channel(log_channel)  # Remplacez par le bon ID de salon
		if log_channel:
			embed = discord.Embed(
				title="🔔 Log de transaction",
				description=f"**Utilisateur :** <@{user}>\n"
							f"**Type :** {change_type}\n"
							f"**Montant :** {amount}\n"
							f"**Motif :** {reason}\n"
							f"**Solde avant :** {before_balance}\n"
							f"**Solde après :** {after_balance}\n"
							f"**Channel :** <#{channel_id}>",
				color=discord.Color.green()
			)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await log_channel.send(embed=embed)

@bot.event
async def on_ready():
    # Met à jour le statut du bot
    activity = discord.Activity(
        name="Gère l'économie du serveur",
        type=discord.ActivityType.playing,  # "Playing" donne un effet similaire
        state="Créer par Bryan.",  # État affiché
        details="Boukistan - RP communautaire"  # Détails supplémentaires
    )

    await bot.change_presence(
        status=discord.Status.online,  # Statut du bot (en ligne)
        activity=activity
    )

    # Envoi d'un message dans le canal de log
    channel = bot.get_channel(log_channel)
    if channel:
        embed = discord.Embed(
            title=f"🎉 {nom_bot} est en ligne !",
            description="",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/707868018708840508/1318353739920183416/RP.png?ex=67620419&is=6760b299&hm=eb566e37869fd02b7a24fa39c8fb0489793ad7e21c9f1c146c0fdec3f3e6db0a&=&format=webp&quality=lossless&width=584&height=584")  # Remplace par l'URL du logo
        embed.add_field(name="🛠 Statut", value="En ligne", inline=True)
        embed.add_field(name="📋 Détails", value=f"{nom_bot} est là pour gérer l'économie du serveur.", inline=True)

        await channel.send(embed=embed)
        print(f"Bot prêt.")

    # Vérification du fichier JSON (mettre cela dans une fonction async)

    check_status = await db_handler.check_json()

    if check_status == "error":
        channel = bot.get_channel(log_channel)  # Vérifiez que log_channel est défini correctement
        color = discord.Color.red()  # ou utilisez une couleur d'erreur personnalisée si définie
        embed = discord.Embed(title=f"Erreur critique. Le fichier JSON est corrompu ou a des variables manquantes.\n\n", description=f"Veuillez contacter un administrateur ou supprimer la base de données JSON, mais faites une sauvegarde avant -\n", color=color)
        embed.add_field(name="", value=f"cela entraînera la recréation de la configuration par défaut, mais aussi **supprimer toutes les données utilisateur**\n\n")
        await channel.send(embed=embed)
        await bot.close()  # Utilisez bot.close() pour fermer proprement le bot

not_done = False
@bot.event
async def on_command_error(ctx, error):
	pass

@bot.event
async def on_message(message):
	if message.author.bot:
		return

	current_time = format_datetime(
		datetime.datetime.now(),
		format="d MMMM y 'à' HH:mm",
		locale="fr_FR"
	)

	global not_done
	last_message = None
	if message.author == bot.user:
		return
	if last_message == message.content:  # Si le message est le même que le précédent
		return
	last_message = message.content

	if not message.content.startswith(BOT_PREFIX):  # Vérifie si le message est vide
		return
	# prefix checked, we can continue
	usedPrefix = message.content[0] # in case we would add more prefixes later
	# in selenor bot : check for case sensitive or not c.s. commands, not needed for this bot,
	# make it a clean input
	command = message.content.split(usedPrefix)[1].lower().split(" ")

	# stop if not meant for bot. (like just a "?")
	if command[0] in ["", " "]: return 0;

	"""
	basically, if the command is :
		+give money blabla
		we take what is after the prefix and before everything else, to just get the command
		in this case : "give"
		edit : for now we just splitted it, pure command will be taken with command = command[0]
	this is to redirect the command to further handling
	"""
	# print(command) # for testing purposes

	param_index = 1
	param = ["none", "none", "none", "none"]
	command_updated = []
	# lets say our command says "remove-item <your mom>"

	try:
		for test_cmd in range(len(command)):
			if command[test_cmd].startswith('"') or command[test_cmd].startswith("'"):
				new_slide = ""
				temp_cmd = test_cmd
				while not(command[temp_cmd].endswith('"') or command[temp_cmd].endswith("'")):
					new_slide += command[temp_cmd] + " "
					temp_cmd += 1
				new_slide += command[temp_cmd]
				command_updated.append(new_slide[1:len(new_slide)-1])
				break
			elif command[test_cmd] in [" ", ""]:
				continue
			else:
				command_updated.append(command[test_cmd])
	except:
			await message.channel.send("Erreur. Vous avez peut-être ouvert un simple/double guillement ou un < et ne l’avez pas fermé")
	command = command_updated
	# print(command)
	for param_index in range(len(command)):
		if param_index < len(param):  # Vérification pour éviter IndexError
			param[param_index] = command[param_index]
	print(f"\033[94mCommande appelée avec les paramètres : {param}\033[0m")
	print(f"Message reçu le {current_time}")
	# for use of parameters later on, will have to start at 0, not 1

	# ~~~~ GET DISCORD VARIABLES for use later on
	# to directly answer in the channel the user called in
	channel = message.channel
	server = message.guild
	user = message.author.id
	user_mention = message.author.mention
	user_pfp = message.author.display_avatar.url
	username = str(message.author)
	nickname = str(message.author.display_name)
	user_roles = [randomvar.id for randomvar in message.author.roles]

	# some stuff will be only for staff, which will be recognizable by the Gérant {nom_bot} role
	roles = [role.name for role in message.author.roles]
	staff_request = "Non Staff"
	for role_to_check in message.author.roles:
		if "Gérant Bot" in roles and "M・Mafieux" in roles: staff_request = "Gérant Bot et Mafieux"
		elif "Gérant Bot" in roles: staff_request = "Gérant Bot"
		elif "Mafieux" in roles: staff_request = "Mafieux"
	print("Statut : ", staff_request)
	command = command[0]

	# --------------
	# PING COMMAND
	# --------------

	if command in ["ping"]:
		latency = round(bot.latency * 1000)  # Convertit en millisecondes
		embed = discord.Embed(title="🏓 Pong !", description=f"Latence : `{latency} ms`", color=discord.Color.blue())
		embed.set_author(name=username, icon_url=user_pfp)
		embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
		await channel.send(embed=embed)
	
	# --------------
	# BLACKJACK GAME
	# --------------

	if command in [ "blackjack", "bj"]:
		if "none" in param[1] or param[2] != "none": # only bj <bet> ; nothing more than that 1 parameter
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`blackjack <amount or all>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		bet = param[1]
		# either all or an amount, not some random string
		if bet != "all":
			try:
				# they can use the thousands separator comma
				newAmount = []
				for char in bet:
					if char != ",":
						newAmount.append(char)
				bet = "".join(newAmount)
				bet = int(bet)
				if bet < 100:
					color = discord_error_rgb_code
					embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`. Le pari doit être d’au moins 100.\n", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
			except:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`.\n\nUsage:\n`roulette <amount or all> <space>`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		bet = str(bet)


		try:
			# gotta check if enough money, if bet enough, etc etc then do the actual game
			status, bj_return = await db_handler.blackjack(user, bet, bot, channel, username, user_pfp, message)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{bj_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		# "success" case where code doesnt fail is answering bot directly in handler
		# same for all other games
		return

	# --------------
	# ROULETTE GAME
	# --------------

	# ATTENTION : for now roulette is only playable by ONE person, multiple can't play at once

	if command in ["roulette", "rl"]:
		if "none" in param[1] or "none" in param[2]:  # we need 2 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`roulette <amount or all> <space>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
	
		bet = param[1]
		if bet != "all":
			try:
				newAmount = [char for char in bet if char != ","]
				bet = "".join(newAmount)
				bet = int(bet)
				if bet < 100:
					color = discord_error_rgb_code
					embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`. Le pari doit être d’au moins 100 Boukens.\n", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
			except:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`.\n\nUsage:\n`roulette <amount or all> <space>`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		bet = str(bet)
	
		space = str(param[2]).lower().strip()
		if space not in ["odd", "even", "noir", "rouge", "black", "red"]:
			fail = 0
			try:
				space = int(space)
				if not (0 <= space <= 36):
					fail = 1
			except Exception as e:
				print(e)
				fail = 1
			if fail == 1:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<space>`.\n\nUsage:\n`roulette <amount or all> <space>`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
	
		if space == "black":
			space = "noir"
		elif space == "red":
			space = "rouge"
	
		try:
			status, roulette_return = await db_handler.roulette(user, bet, space, bot, channel, username, user_pfp, user_mention)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{roulette_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	# 	  SLUT
	# --------------

	if command in ["slut"]:  # no alias
		# Vérifie si l'utilisateur a le rôle "Mafieux" ou "Gérant {nom_bot} et Mafieux"
		if not ("Mafieux" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Mafieux", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		else:
			try:
				status, slut_return = await db_handler.slut(user, channel, username, user_pfp)
	
				if status == "error":
					color = discord_error_rgb_code
					embed = discord.Embed(description=f"{slut_return}", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
			except Exception as e:
				print(e)
				await send_error(channel)

	# -------------------
	# 	  ADVENTURE
	# -------------------
	
	if command in ["adventure", "aventure", "adv", "av"]:
		if "Mafieux" in staff_request or "Gérant Bot} et Mafieux" in staff_request:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Cette commande n'est pas accessible aux Mafieux", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		else:
			try:
				status, adventure_return = await db_handler.adventure(user, channel, username, user_pfp)
				if status == "error":
					color = discord_error_rgb_code
					embed = discord.Embed(description=f"{adventure_return}", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
			except Exception as e:
				print(e)
				await send_error(channel)
	
	# --------------
	# 	  CRIME
	# --------------

	if command in ["crime"]:  # no alias
		if not ("Mafieux" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Mafieux", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		
		try:
			status, crime_return = await db_handler.crime(user, channel, username, user_pfp)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{crime_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	# 	  WORK
	# --------------

	if command in ["work"]:  # no alias
		try:
			status, work_return = await db_handler.work(user, channel, username, user_pfp)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{work_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	# 	  ROB
	# --------------

	if command in ["rob", "steal"]:  # no alias
		if not ("Mafieux" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Mafieux", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		
		if "none" in param[1] or param[2] != "none": # we only one param
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`rob <user>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		user_to_rob = await get_user_id(param)

		try:
			status, rob_return = await db_handler.rob(user, channel, username, user_pfp, user_to_rob)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{rob_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	#    BALANCE
	# --------------

	if command in ["balance", "bal", "bl"]:		
		# you can either check your own balance or someone else's bal
		if "none" in param[1]:
			# tell handler to check bal of this user
			userbal_to_check = user
			username_to_check = username
			userpfp_to_check = user_pfp
		# only one user to check, so only 1 param, if 2 -> error
		elif param[1] != "none" and param[2] != "none":
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `[user]`.\n\nUsage:\n`balance <user>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		# else we want the balance of someone else
		else:
			userbal_to_check = await get_user_id(param)
			try:
				user_fetch = bot.get_user(int(userbal_to_check))
				username_to_check = user_fetch
				userpfp_to_check = user_fetch.avatar
			except:
				# we didnt find him
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `[user]`.\n\nUsage:\n`balance <user>`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		# go through the handler
		try:
			await db_handler.balance(user, channel, userbal_to_check, username_to_check, userpfp_to_check, not_done)
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	# 	  DEP
	# --------------

	elif command in ["deposit", "dep", "dp"]:
		if "none" in param[1] or param[2] != "none": # we need 1 and only 1 parameter
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`deposit <amount or all>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		amount = param[1]
		# either all or an amount, not some random string
		if amount != "all":
			try:
				# they can use the thousands separator comma
				newAmount = []
				for char in amount:
					if char != ",":
						newAmount.append(char)
				amount = "".join(newAmount)
				amount = int(amount)
				if amount < 1:
					color = discord_error_rgb_code
					embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`.\n\nUsage:\n`deposit <amount or all>`", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
			except:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`.\n\nUsage:\n`deposit <amount or all>`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		try:
			amount = str(amount)
			status, dep_return = await db_handler.deposit(user, channel, username, user_pfp, amount)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{dep_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	# 	  WITH
	# --------------

	elif command in ["withdraw", "with"]:
		if "none" in param[1] or param[2] != "none": # we need 1 and only 1 parameter
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`withdraw <amount or all>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		amount = param[1]
		# either all or an amount, not some random string
		if amount != "all":
			try:
				# they can use the thousands separator comma
				newAmount = []
				for char in amount:
					if char != ",":
						newAmount.append(char)
				amount = "".join(newAmount)
				amount = int(amount)
				if amount < 1:
					color = discord_error_rgb_code
					embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`.\n\nUsage:\n`withdraw <amount or all>`", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
			except:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`.\n\nUsage:\n`withdraw <amount or all>`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		try:
			amount = str(amount)
			status, with_return = await db_handler.withdraw(user, channel, username, user_pfp, amount)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{with_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	# 	  GIVE
	# --------------

	elif command in ["give", "pay"]:
		if "none" in param[1] or "none" in param[2]:  # we need 2 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(
				description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`give <member> <amount or all>`\nInfo : pour les items utilisez `give-item` !",
				color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# we need to check validity of both parameters

		# CHECK 1

		reception_user = await get_user_id(param)

		try:
			user_fetch = bot.get_user(int(reception_user))
			print(user_fetch)
			reception_user_name = user_fetch

			if int(reception_user) == user:
				# cannot send money to yourself
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Vous ne pouvez pas échanger de l’argent avec vous-même. Ce serait inutile.\n"
												  f"(Vous recherchez peut-être la commande `add-money`.)", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		except:
			# we didnt find him
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<member>`.\n\nUsage:"
											  f"\n`give <member> <amount or all>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# CHECK 2

		amount = param[2]
		# either all or an amount, not some random string
		if amount != "all":
			try:
				# they can use the thousands separator comma
				newAmount = []
				for char in amount:
					if char != ",":
						newAmount.append(char)
				amount = "".join(newAmount)
				amount = int(amount)
				if amount < 1:
					color = discord_error_rgb_code
					embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount or all>`.\n\nUsage:\n`give <member> <amount or all>`", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
			except:
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Argument donné non valide `<amount or all>`.\n\nUsage:\n`give <member> <amount or all>`",
					color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		# handler

		try:
			amount = str(amount)
			status, give_return = await db_handler.give(user, channel, username, user_pfp, reception_user, amount, reception_user_name)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{give_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	#  LEADERBOARD
	# --------------

	elif command in ["leaderboard", "lb"]:
		modes = ["-cash", "-bank", "-total"]
		page_number = 1
		mode_type = modes[2]
		server_name = server.name
		full_name = server_name  # + mode_type

		# first, vanilla
		if "none" in param[1] and "none" in param[2]:
			# using default vars
			page_number = 1
			mode_type = modes[2]
			full_name += " Leaderboard"
		# one argument
		elif param[1] != "none" and "none" in param[2]:
			if param[1] in modes:
				mode_type = param[1]
				page_number = 1
				if mode_type == "-total": full_name += " Leaderboard"
				if mode_type == "-cash": full_name += " Cash Leaderboard"
				if mode_type == "-bank": full_name += " Bank Leaderboard"
			else:
				try:
					page_number = int(param[1])
					mode_type = modes[2]
					full_name += " Leaderboard"
				except:
					color = discord_error_rgb_code
					embed = discord.Embed(
						description=f"{emoji_error}  Argument donné non valide `[-cash | -bank | -total]`.\n\nUsage:\n"
									f"`leaderboard [page] [-cash | -bank | -total]`", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
		# two arguments
		else:
			try:
				page_number = int(param[1])
				mode_type = param[2]
				if mode_type == "-total": full_name += " Leaderboard"
				elif mode_type == "-cash": full_name += " Cash Leaderboard"
				elif mode_type == "-bank": full_name += " Bank Leaderboard"
				else:
					color = discord_error_rgb_code
					embed = discord.Embed(
						description=f"{emoji_error}  Argument donné non valide `[-cash | -bank | -total]`.\n\nUsage:\n"
									f"`leaderboard [page] [-cash | -bank | -total]`", color=color)
					embed.set_author(name=username, icon_url=user_pfp)
					embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await channel.send(embed=embed)
					return
			except:
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Argument donné non valide `[-cash | -bank | -total]`.\n\nUsage:\n"
								f"`leaderboard [page] [-cash | -bank | -total]`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		# handler

		try:
			status, lb_return = await db_handler.leaderboard(user, channel, username, full_name, page_number, mode_type, bot)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{lb_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	#     HELP
	# --------------

	elif command in ["help", "info"]:
		color = discord.Color.from_rgb(3, 169, 244)
		embed = discord.Embed(title=f"Toutes les commandes de {nom_bot} PART1", color=color)
		embed.add_field(name="Afficher les stats du serveur", value=f"`+stats`", inline=False)
		embed.add_field(name="Jouer au blackjack", value=f"`+blackjack <amount or all>`"f"\nou `+bj`", inline=True)
		embed.add_field(name="Jouer a la roulette", value=f"`+roulette <amount or all> <space>`"f"\nou `+rl`", inline=True)
		embed.add_field(name="Travailler", value=f"`+work`", inline=True)
		embed.add_field(name="Voler", value=f"`+rob`"f"\nou `+steal`", inline=True)
		embed.add_field(name="Catin", value=f"`+slut`", inline=True)
		embed.add_field(name="Faire un crime", value=f"`+crime`", inline=True)
		embed.add_field(name="Partir a l'aventure", value=f"`+adventure`"f"\nou `+adv`", inline=True)
		embed.add_field(name="Afficher votre solde", value=f"`+balance`"f"\nou `+bal`", inline=True)
		embed.add_field(name="Déposer de l'argent a la banque", value=f"`+deposit <amount>`"f"\nou `+dep`", inline=True)
		embed.add_field(name="Retirer de l'argent de la banque", value=f"`+withdraw <amount>`"f"\nou `+with`", inline=True)
		embed.add_field(name="Donner de son argent a quelqu'un", value=f"`+give <member> <amount or all>`"f"\nou `+pay`", inline=True)
		embed.add_field(name="Afficher le classement de l'argent du serveur", value=f"`+leaderboard [page] [-cash | -bank | -total]`"f"\nou `+lb`", inline=True)
		embed.add_field(name="Afficher ces messages d'aide", value=f"`+help`"f"\nou `+info`", inline=True)
		embed.add_field(name="Contrôler les différents modules du bot", value=f"`+module <module, ex : work>`"f"\nou `+moduleinfo`", inline=True)
		
		# edit stuff
		await channel.send(embed=embed)

		#### in 2 parts because one was too long

		embed = discord.Embed(title=f"Toutes les commandes de {nom_bot} PART2", color=color)
		embed.add_field(name="Ajouter de l'argent", value=f"`+add-money <member> <amount>`", inline=True)
		embed.add_field(name="Retirer de l'argent", value=f"`+remove-money <member> <amount> [cash/bank]`", inline=True)
		embed.add_field(name="Supprime de l'argent à un rôle", value=f"`+remove-money-role <role> <amount>`", inline=True)
		embed.add_field(name="Modifier la variable d'un module", value=f"`+change <module> <variable> <new value>`", inline=True)
		embed.add_field(name="Changer la devise du Bot", value=f"`+change-currency <new emoji name>`", inline=True)
		embed.add_field(name="Set income reset", value=f"`+set-income-reset <false/true>`", inline=True)
		embed.add_field(name="Retirer un item a quelqu'un", value=f"`+remove-user-item <member> <item short name> <amount>`", inline=True)
		embed.add_field(name="Ajouter un item a quelqu'un", value=f"`+spawn-item <player pinged> <item short name> [amount]`", inline=True)
		embed.add_field(name="Met à jour le classement", value=f"`+clean-leaderboard`", inline=True)
		embed.add_field(name="----------------------\n\nGESTION DES ITEMS", value="", inline=False)
		embed.add_field(name="Créer un item", value=f"`+create-item`", inline=True)
		embed.add_field(name="Supprimer un item", value=f"`+delete-item <item short name>`", inline=True)
		embed.add_field(name="Acheter un item", value=f"`+buy-item <item short name> <amount>`", inline=True)
		embed.add_field(name="Donner un item", value=f"`+give-item <member> <item short name> <amount>`", inline=True)
		embed.add_field(name="Utiliser un item", value=f"`+use <item short name> <amount>`", inline=True)
		embed.add_field(name="Ouvrir son inventaire", value=f"`+inventory [page]`", inline=True)
		embed.add_field(name="Ouvrir l'inventaire d'un utilisateur", value=f"`+user-inventory <member> [page]`", inline=True)
		embed.add_field(name="Ouvrir la boutique du serveur", value=f"`+catalog [item short name]`"f"\nou `+shop`", inline=True)
		embed.add_field(name="----------------------\n\nROLES LIEES AU SALAIRE", value="", inline=False)
		embed.add_field(name="Ajouter un role a salaire", value=f"`+add-income-role <role pinged> <income>`", inline=True)
		embed.add_field(name="Retirer un role avec salaire", value=f"`+remove-income-role <role pinged>`", inline=True)
		embed.add_field(name="Affiche la liste des roles avec salaire", value=f"`+list-roles`", inline=True)
		embed.add_field(name="Recolter votre salaire", value=f"`+collect`", inline=True)
		embed.add_field(name="Mettre a jour un salaire", value=f"`+update-income`", inline=True)
		embed.set_footer(text=f"Pour plus d'infos demandez de l'aide à un membre du staff ou à @Bryan_Drouet.\n{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
		await channel.send(embed=embed)

	# --------------
	#  MODULE INFO
	# --------------

	elif command in ["module", "moduleinfo"]:
		if "none" in param[1] or param[2] != "none":  # we need 1 and only 1 parameter
			color = discord_error_rgb_code
			embed = discord.Embed(
				description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`module <module>`",
				color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		module = param[1]

		# handler

		try:
			status, module_return = await db_handler.module(user, channel, module)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{module_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

		"""
			STAFF COMMANDS
		"""

	# --------------
	#   ADD-MONEY
	# --------------

	elif command == "add-money":
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1] or "none" in param[2]:  # we need 2 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`add-money <member> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# we need to check validity of both parameters

		# CHECK 1

		reception_user = await get_user_id(param)
		try:
			user_fetch = bot.get_user(int(reception_user))
			print(user_fetch)
			reception_user_name = user_fetch

		except:
			# we didnt find him
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<member>`.\n\nUsage:"
											  f"\n`add-money <member> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# CHECK 2

		amount = param[2]
		try:
			# they can use the thousands separator comma
			newAmount = []
			for char in amount:
				if char != ",":
					newAmount.append(char)
			amount = "".join(newAmount)
			amount = int(amount)
			if amount < 1:
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Argument donné non valide `<amount>`.\n\nUsage:\n`add-money <member> <amount>`",
					color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount>`.\n\nUsage:\n`add-money <member> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# handler

		try:
			amount = str(amount)
			status, add_money_return = await db_handler.add_money(user, channel, username, user_pfp, reception_user, amount, reception_user_name)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{add_money_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	#  REMOVE-MONEY
	# --------------

	elif command == "remove-money":
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1] or "none" in param[2]:  # we need 3 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`remove-money <member> <amount> [cash/bank]`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# we need to check validity of both parameters

		# CHECK 1

		reception_user = await get_user_id(param)

		try:
			user_fetch = bot.get_user(int(reception_user))
			print(user_fetch)
			reception_user_name = user_fetch

		except:
			# we didnt find him
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<member>`.\n\nUsage:"
											  f"\n`remove-money <member> <amount> [cash/bank]`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# CHECK 2

		amount = param[2]
		try:
			# they can use the thousands separator comma
			newAmount = []
			for char in amount:
				if char != ",":
					newAmount.append(char)
			amount = "".join(newAmount)
			amount = int(amount)
			if amount < 1:
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Argument donné non valide `<amount>`.\n\nUsage:\n`remove-money <member> <amount> [cash/bank]`",
					color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount>`.\n\nUsage:\n`remove-money <member> <amount> [cash/bank]`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# CHECK 3
		mode = "bank"
		if param[3] != "none":
			if param[3] in ["cash", "bank"]:
				mode = param[3]
			else:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `[cash/bank]`.\n\nUsage:"
												  f"\n`remove-money <member> <amount> [cash/bank]`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		# handler

		try:
			amount = str(amount)
			status, rm_money_return = await db_handler.remove_money(user, channel, username, user_pfp, reception_user, amount, reception_user_name, mode)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{rm_money_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# --------------
	#   EDIT VARS
	# --------------

	elif command in ["change", "edit"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1] or "none" in param[2] or "none" in param[3]:  # we need 3 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`change <module> <variable> <new value>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# that would end up messing everything up
		if param[2] == "name":
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Vous ne pouvez pas changer les noms de module.", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# we need to check validity of new value parameter
		# other checks will be done in the handler

		# CHECK
		module_name = param[1]
		variable_name = param[2]
		new_value = param[3]
		try:
			new_value = int(new_value)
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<new value>`.\n\nUsage:\n`change <module> <variable> <new value>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# handler

		try:
			new_value = str(new_value)
			status, edit_return = await db_handler.edit_variables(user, channel, username, user_pfp, module_name, variable_name, new_value)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{edit_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# ---------------------------
	#   CHANGE CURRENCY SYMBOL
	# ---------------------------

	elif command in ["change-currency", "edit_currency"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1]:  # we need 1 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`change-currency <new emoji name>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		new_emoji_name = param[1]

		# handler

		try:
			status, emoji_edit_return = await db_handler.change_currency_symbol(user, channel, username, user_pfp, new_emoji_name)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_edit_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# ---------------------------
	#   SET INCOME RESET
	# ---------------------------

	elif command in ["set-income-reset", "change-income-reset"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1]:  # we need 1 parameter
			color = discord_error_rgb_code
			embed = discord.Embed(
				description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage: `set-income-reset <false/true>`",
				color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if param[1] not in ["true", "false"]:  # and that param has to be true/false
			color = discord_error_rgb_code
			embed = discord.Embed(
				description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage: `set-income-reset <false/true>`",
				color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# ok so all checks done
		new_income_reset = param[1]

		# handler
		try:
			status, new_income_reset_return = await db_handler.set_income_reset(user, channel, username, user_pfp,
																				new_income_reset)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{new_income_reset_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)


		"""
			SPECIAL COMMANDS
		"""

	# ---------------------------
	#   ITEM CREATION / Create item
	# ---------------------------

	elif command in ["create-item", "new-item", "item-create"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		currently_creating_item = True
		checkpoints = 0
		last_report = ""
		color = discord.Color.from_rgb(3, 169, 244)
		# send a first input which we will then edit
		info_text = ":zero: Quel doit être le nom du nouvel article?\nCe nom doit être unique et ne pas dépasser 200 caractères.\nIl peut contenir des symboles et plusieurs mots."
		first_embed = discord.Embed(title="Infos de l'Item", description="Nom d'affichage\n.", color=color)
		first_embed.set_footer(text="Taper ``cancel`` pour quitter")
		await channel.send(info_text, embed=first_embed)

		while currently_creating_item:
			# get input first
			user_input = await get_user_input(message, default_spell=False)
			print("réponse", checkpoints, "\n", user_input)
			# check if user wants cancel
			if user_input == "cancel":
				await channel.send(f"{emoji_error}  Commande annulée.")
				return

			if checkpoints == 0:
				# check 0: display name
				if len(user_input) > 200:
					await channel.send(f"{emoji_error} La longueur maximale d’un nom d'item est de 200 caractères. Veuillez réessayer.")
					continue
				elif len(user_input) < 3:
					await channel.send(f"{emoji_error}  La longueur minimale d’un nom d'item est de 3 caractères. Veuillez réessayer.")
					continue
				# good input
				item_display_name = user_input
				first_embed = discord.Embed(title="Infos de l'Item", color=color)
				first_embed.add_field(name="Nom d'affichage", value=f"{item_display_name}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter")
				next_info = ":one: Il nous faut maintenant un nom court, que les utilisateurs utiliseront pour acheter, donner etc. Un seul mot ! (vous pouvez utiliser des tirets et des underscores)"
				last_report = await channel.send(next_info, embed=first_embed)
				checkpoints += 1
				#item_name = await get_user_input(message)
				#print(item_name)
				trial = 0

			if checkpoints == 1:
				trial +=1
				item_name = await get_user_input(message) if trial == 1 else user_input

				# check 1: name
				if len(item_name) > 10:
					await channel.send(f"{emoji_error} La longueur maximale pour un nom court d'item est de 10 caractères. Veuillez réessayer.")
					continue
				elif len(item_name) < 3:
					await channel.send(f"{emoji_error}  La longueur minimale pour un nom court d'item est de 3 caractères. Veuillez réessayer.")
					continue
				elif " " in item_name.strip():
					print(f"-{item_name}- -{item_name.strip()}")
					await channel.send(f"{emoji_error}  le nom court doit être UN SEUL mot (tirets ou underscore).")
					continue
				# good input
				first_embed.add_field(name="Nom court", value=f"{item_name}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter")
				next_info = ":two: Combien doit coûter l’article à acheter?"
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 2:
				# check 2: cost
				try:
					cost = int(user_input)
					if cost < 1:
						await channel.send(f"{emoji_error}  Prix invalide indiqué. Veuillez réessayer ou taper ``cancel`` pour quitter.")
						continue
				except:
					await channel.send(f"{emoji_error}  Prix invalide indiqué. Veuillez réessayer ou taper ``cancel`` pour quitter.")
					continue
				first_embed.add_field(name="Prix", value=f"{cost}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = ":three: Veuillez fournir une description de l’article.\nIl ne doit pas dépasser 200 caractères."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 3:
				# check 3: description
				if len(user_input) > 1000:
					await channel.send(f"{emoji_error} La longueur maximale pour une description d'item est de 1000 caractères. Veuillez réessayer.")
					continue
				if user_input.lower() == "skip":
					description = "none"
				else:
					description = user_input
				first_embed.add_field(name="Description", value=f"{description}", inline=False)
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = ":four: Combien de temps cet article doit-il rester dans le magasin? (nombre entier, en jours)\nLa durée minimale est de 1 jour.\nSi aucune limite, répondez simplement ``skip``."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 4:
				# check 4: duration
				try:
					duration = int(user_input)
					if duration < 1:
						await channel.send(f"{emoji_error}  Durée de temps invalide donnée. Veuillez réessayer ou taper ``cancel`` pour quitter.")
						continue
				except:
					if user_input.lower() == "skip":
						#duration = "none"
						duration = 99999 # the problem is that database.py always wants an int to calculate an expiration date.
									   # so ill just put it to 993 days for now, maybe ill add a real fix later
									   # edit: now changed to 99999 which should be enough, will show as "unlimited"
					else:
						await channel.send(f"{emoji_error}  Durée de temps invalide donnée. Veuillez réessayer ou taper ``cancel`` pour quitter.")
						continue
				if duration == 99999:
					duration_str = "unlimited"
				else:
					duration_str = int(user_input)
				first_embed.add_field(name="Temps restant", value=f"{duration} jours restants")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = ":five: Combien de stock de cet article sera-t-il disponible?\nSi illimité, répondez simplement ``skip`` ou ``infinity``."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1
			elif checkpoints == 5:
				# check 5: stock
				try:
					stock = int(user_input)
					if stock < 1:
						await channel.send(f"{emoji_error}  Valeur de stock non valide. Veuillez réessayer ou taper cancel pour quitter.")
						continue
				except:
					if user_input.lower() == "skip" or user_input.lower() == "infinity":
						stock = "unlimited"
					else:
						await channel.send(f"{emoji_error}   Valeur de stock non valide. Veuillez réessayer ou taper cancel pour quitter.")
						continue

				first_embed.add_field(name="Stock restant", value=f"{stock}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = ":six: Quel est le montant MAX de cet article par utilisateur qui devrait être autorisé ?\nSi aucun, répondez simplement `skip`."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 6:
				# check 6: max amount of item
				try:
					max_amount = int(user_input)
					if max_amount < 1:
						await channel.send(f"{emoji_error}  Montant maximal indiqué non valide. Veuillez réessayer ou taper cancel pour quitter.")
						continue
				except:
					if user_input.lower() == "skip" or user_input.lower() == "infinity":
						max_amount = "unlimited"
					else:
						await channel.send(f"{emoji_error}  Montant maximal indiqué non valide. Veuillez réessayer ou taper cancel pour quitter.")
						continue

				first_embed.add_field(name="Montant maxiumum", value=f"{max_amount}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = ":seven: Quel rôle(s) l’utilisateur doit-il déjà avoir pour acheter cet article?\nSi aucun, répondez simplement ``skip``. Pour les multiples, faites un ping des rôles avec un espace entre eux."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 7:
				# check 7: required role
				try:
					if user_input in ["skip", "none"]:
						raise ValueError

					roles_clean_one = await get_role_id_multiple(user_input)

					required_roles = ""
					for role_id in roles_clean_one:
						try:
							role = discord.utils.get(server.roles, id=int(role_id))
							print(role)
							required_roles += f"{str(role.mention)} "
						except:
							await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
							raise NameError

				except NameError:
					continue

				except ValueError:
					if user_input in ["skip", "none"]:
						required_roles = ["none"]

				except Exception as e:
					await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
					continue
				try:
					roles_id_required = roles_clean_one
					print(roles_id_required)
				except:
					roles_id_required = ["none"]
				first_embed.add_field(name="Role requis", value=f"{required_roles}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = ":eight: Quels rôles devraient rendre l’achat de cet article impossible? (rôle(s) exclu)?\nSi aucun, répondez simplement ``skip``. Pour les multiples, faites un ping avec un espace entre elles."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1
				
			elif checkpoints == 8:
				# check 8: excluded role - meaning you cant buy if possessing it.
				try:
					if user_input in ["skip", "none"]:
						raise ValueError

					roles_clean_two = await get_role_id_multiple(user_input)

					excluded_roles = ""
					for role_id in roles_clean_two:
						try:
							role = discord.utils.get(server.roles, id=int(role_id))
							print(role)
							excluded_roles += f"{str(role.mention)} "
						except:
							await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
							raise NameError

				except NameError:
					continue

				except ValueError:
					if user_input in ["skip", "none"]:
						excluded_roles = ["none"]

				except Exception as e:
					await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
					continue
				try:
					roles_id_excluded = roles_clean_two
					print(roles_id_excluded)
				except:
					roles_id_excluded = ["none"]
				first_embed.add_field(name="Rôles donnés", value=f"{excluded_roles}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = ":nine: Quel(s) rôle voulez-vous être donné lorsque cet article est acheté?\nSi aucun, répondez simplement ``skip``. Pour les multiples, faites un ping avec un espace entre elles."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 9:
				# check 9: role to be given when item bought
				try:
					if user_input in ["skip", "none"]:
						raise ValueError

					roles_clean_three = await get_role_id_multiple(user_input)

					roles_give = ""
					for role_id in roles_clean_three:
						try:
							role = discord.utils.get(server.roles, id=int(role_id))
							print(role)
							roles_give += f"{str(role.mention)} "
						except:
							await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
							raise NameError

				except NameError:
					continue

				except ValueError:
					if user_input in ["skip", "none"]:
						roles_give = ["none"]

				except Exception as e:
					await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
					continue

				try:
					roles_id_to_give = roles_clean_three
				except:
					roles_id_to_give = ["none"]
				first_embed.add_field(name="Role à donner", value=f"{roles_give}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = ":keycap_ten: Quel(s) rôle(s) voulez-vous que l’utilisateur retire lorsqu’il achète cet article?\nSi aucun, répondez simplement ``skip``. Pour les multiples, faites un ping avec un espace entre elles."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 10:
				# check 10: role to be removed when item bought
				try:
					if user_input in ["skip", "none"]:
						raise ValueError

					roles_clean_four = await get_role_id_multiple(user_input)

					roles_remove = ""
					for role_id in roles_clean_four:
						try:
							role = discord.utils.get(server.roles, id=int(role_id))
							print(role)
							roles_remove += f"{str(role.mention)} "
						except:
							await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
							raise NameError

				except NameError as b:
					print(b)
					continue

				except ValueError:
					if user_input in ["skip", "none"]:
						roles_remove = ["none"]

				except Exception as e:
					await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
					continue

				try:
					roles_id_to_remove = roles_clean_four
				except:
					roles_id_to_remove = ["none"]
				first_embed.add_field(name="Role à retirer", value=f"{roles_remove}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = "`11` Quel est le maximum de balance qu’un utilisateur peut avoir pour acheter cet article ?\nSi aucun, répondez simplement ``skip``."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 11:
				# check 11: max balance
				try:
					max_bal = int(user_input)
					if max_bal < 1:
						await channel.send(f"{emoji_error}  Solde maximal non valide. Veuillez réessayer ou taper ``cancel`` pour quitter.")
						continue
				except:
					if user_input.lower() == "skip":
						max_bal = "none"
					else:
						await channel.send(f"{emoji_error}  Solde maximal non valide. Veuillez réessayer ou taper ``cancel`` pour quitter.")
						continue
				first_embed.add_field(name="Balance maximale", value=f"{max_bal}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = "`12`: Quel message voulez-vous que le bot réponde lorsque l’article est acheté?\nSi aucun, répondez simplement ``skip``."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 12:
				# check 12: reply message
				if len(user_input) > 150:
					await channel.send(f"{emoji_error} La longueur maximale d’un message de réponse est de 150 caractères. Veuillez réessayer.")
					continue
				if user_input.lower() == "skip":
					user_input = f"Merci d'avoir acheter cet article."
				reply_message = user_input
				first_embed.add_field(name="Message de réponse", value=f"{reply_message}", inline=False)
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = "`13`: L'article est-il vendu par quelqu'un en particulier ?\nSi aucun, répondez simplement ``skip``."
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 13:
				try:
					# Si l'utilisateur veut sauter ou ignorer cette étape
					if user_input in ["skip", "none"]:
						raise ValueError
			
					# Validation : S'assurer qu'il n'y a qu'une seule mention ou ID
					user_inputs = user_input.split()
					if len(user_inputs) > 1:
						await channel.send(f"{emoji_error} Veuillez entrer **une seule** mention ou un identifiant.")
						continue
			
					# Extraire l'ID utilisateur à partir de la mention ou de l'entrée
					user_id = await get_user_id(user_inputs)
					print(f"ID utilisateur extrait : {user_id}")  # Debugging
			
					# Récupération du membre à partir de l'ID
					try:
						user = await server.fetch_member(int(user_id))  # Récupération du membre par son ID
						print(f"Utilisateur trouvé : {user}")  # Debugging
						vendeur = user.mention  # Générer la mention
					except Exception as fetch_error:
						print(f"Erreur lors de fetch_member : {fetch_error}")  # Debugging
						await channel.send(f"{emoji_error}  Le membre attribué n’est pas valide ou introuvable. Veuillez réessayer.")
						raise NameError
			
				except NameError:
					continue
			
				except ValueError:
					# Gestion de l'étape "skip" ou "none"
					if user_input in ["skip", "none"]:
						vendeur = "none"
					else:
						await channel.send(f"{emoji_error}  Une erreur de valeur est survenue.")
						continue
			
				except Exception as e:
					print(f"Erreur inattendue : {e}")  # Debugging
					await channel.send(f"{emoji_error}  Une erreur s'est produite. Veuillez réessayer.")
					continue
			
				# Ajout de l'utilisateur dans l'embed
				first_embed.add_field(name="Vendeur", value=f"{vendeur}")
				first_embed.set_footer(text="Taper ``cancel`` pour quitter ou ``skip`` pour sauter cette option")
				next_info = "`14`: Quelle image doit avoir l’article? Entrez l’URL complète !\nSi aucun, répondez simplement ``skip``"
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints += 1

			elif checkpoints == 14:
				# check 13: item img
				if user_input.lower() == "skip":
					user_input = f"EMPTY"
					item_img_url = user_input
				else:
					try:
						rq = requests.get(user_input)
					except:
						await channel.send(f"{emoji_error} URL non trouvée. Veuillez réessayer ou ignorer.")
						continue
	
					if rq.status_code != 200:
						await channel.send(f"{emoji_error} URL non trouvée. Veuillez réessayer ou ignorer.")
						continue
					item_img_url = user_input
					first_embed.set_thumbnail(url=item_img_url)
				next_info = f"{emoji_worked}  Article créé avec succès!"
				await last_report.edit(content=next_info, embed=first_embed)
				checkpoints = -1
				# finished with the checks
				currently_creating_item = False


		# handler

		try:
			status, create_item_return = await db_handler.create_new_item(item_display_name, item_name, cost, description, duration, stock, max_amount, roles_id_required, roles_id_to_give, roles_id_to_remove, max_bal, reply_message, item_img_url, roles_id_excluded, vendeur)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{create_item_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

	# ---------------------------
	#   DELETE ITEM - REMOVE ITEM
	# ---------------------------

	elif command in ["delete-item", "remove-item"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1]:  # we need 1 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`delete-item <item short name>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		item_name = param[1]

		# since this will completely remove the item
		# we should make sure you rly want to do this (and not remove-user-item).
		security_check = False
		sec_embed = discord.Embed(title="Attention", description="🚨 Cela supprimera définitivement l’élément, également pour chaque utilisateur!\nVoulez-vous continuer ? [y/N]", color=discord.Color.from_rgb(3, 169, 244))
		sec_embed.set_footer(text="Info : utiliser remove-user-item pour supprimer un élément d’un utilisateur spécifique.")
		await channel.send(embed=sec_embed)

		security_check_input = await get_user_input(message)
		if security_check_input.strip().lower() not in ["yes", "y"]:
			await channel.send(f"{emoji_error}  Commande annulée.")
			return

		# handler

		try:
			status, remove_item_return = await db_handler.remove_item(item_name)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{remove_item_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

		color = discord.Color.from_rgb(102, 187, 106) # green
		embed = discord.Embed(description=f"{emoji_worked}  L’article a été retiré du magasin.\nRemarque : supprime également de l’inventaire de tout le monde.", color=color)
		embed.set_author(name=username, icon_url=user_pfp)
		embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
		await channel.send(embed=embed)

		return

	# ---------------------------
	#   REMOVE USER ITEM
	# ---------------------------

	elif command in ["remove-user-item"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1]:  # we need player pinged
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`remove-user-item <member> <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		player_ping = await get_user_id(param)

		try:
			user_fetch = bot.get_user(int(player_ping))
			print(user_fetch)
			reception_user_name = user_fetch
		except:
			# we didnt find him
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<member>`.\n\nUsage:"
											  f"\n`remove-user-item <member> <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[2]:  # we need item name
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`remove-user-item <member> <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		item_name = param[2]

		if "none" in param[3]:  # we need item amount
			amount = 1
		else:
			amount = param[3]

		try:
			amount = int(amount)
			if amount < 1:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `amount`.\n\nUsage:\n`remove-user-item <member> <item short name> <amount>", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `amount`.\n\nUsage:\n`remove-user-item <member> <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# handler

		try:
			status, remove_user_item_return = await db_handler.remove_user_item(user, channel, username, user_pfp, item_name, amount, player_ping, reception_user_name)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{remove_user_item_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return
	
	# ---------------------------
	#   REMOVE GONE USERS
	# ---------------------------

	elif command in ["clean-leaderboard", "clean-lb"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# since this will completely remove those users
		# we should make sure you rly want to do this.
		security_check = False
		sec_embed = discord.Embed(title="Attention", description="🚨 Cela supprimera définitivement toutes les instances utilisateur qui ont quitté le serveur !\nVoulez-vous continuer ? [y/N]", color=discord.Color.from_rgb(3, 169, 244))
		await channel.send(embed=sec_embed)

		security_check_input = await get_user_input(message)
		if security_check_input.strip().lower() not in ["yes", "y"]:
			await channel.send(f"{emoji_error}  Commande annulée.")
			return

		# handler

		try:
			status, clean_lb_return = await db_handler.clean_leaderboard(server)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{clean_lb_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
			return

		color = discord.Color.from_rgb(102, 187, 106) # green
		embed = discord.Embed(description=f"{emoji_worked} {clean_lb_return} utilisateur(s) ont été supprimés de la base de données.", color=color)
		embed.set_author(name=username, icon_url=user_pfp)
		embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
		await channel.send(embed=embed)

		return

	# ---------------------------
	#   BUY ITEM
	# ---------------------------
	
	elif command in ["buy-item", "get-item", "buy"]:
		# Vérification des paramètres
		if "none" in param[1]:  # Nom de l'item requis
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error} Trop peu d’arguments donnés.\n\nUsage:\n`buy-item <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		item_name = param[1]
	
		if "none" in param[2]:  # Quantité de l'item
			amount = 1
		else:
			amount = param[2]
	
		# Validation de la quantité
		try:
			amount = int(amount)
			if amount < 1:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error} Argument donné non valide `amount`.\n\nUsage:\n`buy-item <item short name> <amount>`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error} Argument donné non valide `amount`.\n\nUsage:\n`buy-item <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
	
		# Handler de l'achat
		user_role_ids = [randomvar.id for randomvar in message.author.roles]
	
		try:
			# Appel à la fonction de gestion d'achat (achat dans la base de données, validation, etc.)
			status, buy_item_return = await db_handler.buy_item(user, channel, username, user_pfp, item_name, amount, user_role_ids, server, message.author)
			
			# Débogage - Vérification des données retournées
			print(f"Valeur retournée par `db_handler.buy_item`: {buy_item_return}")
			print(f"Type de `buy_item_return`: {type(buy_item_return)}")
			
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{buy_item_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
	
			# Vérification du type de `buy_item_return`
			if isinstance(buy_item_return, dict):
				item_info = buy_item_return
			elif isinstance(buy_item_return, str):
				# Si c'est une chaîne, l'interpréter comme un message de succès minimal
				item_info = {"vendeur": "none", "price": 0}
			else:
				print(f"Erreur: Type inattendu pour `buy_item_return`. Valeur: {buy_item_return}")
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error} Une erreur inattendue est survenue lors du traitement de l'achat.", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
	
			vendeur_mention = item_info.get("vendeur", "none")
			price = item_info.get("price", 0)
			vendeur_name = "Inconnu"
	
			# Débogage - Vérification du vendeur
			print(f"Débogage - Vendeur mention: {vendeur_mention}")
	
			if vendeur_mention == "none":
				# Si aucun vendeur n'est trouvé, informer l'utilisateur
				print("Aucun vendeur associé à cet achat.")
				color = discord.Color.green()
				embed = discord.Embed(description=f"{emoji_worked} Achat de **{item_name}** effectué avec succès pour {price * amount} Boukens. Aucun vendeur assigné.", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
	
			# Si l'item a un vendeur
			# Extraire l'ID du vendeur à partir de la mention
			vendeur_id = vendeur_mention.strip('<@>').strip('!')
	
			# Débogage - Vérification de l'ID extrait
			print(f"Débogage - ID extrait: {vendeur_id}")
	
			if not vendeur_id.isdigit():
				print(f"Erreur: ID du vendeur non valide - {vendeur_id}")
				vendeur_mention = "none"
			else:
				try:
					# Récupérer l'objet utilisateur (vendeur) via son ID
					vendeur = await server.fetch_member(int(vendeur_id))  # Recherche du membre par ID
					vendeur_name = vendeur.name if vendeur else "Inconnu"
	
					# Débogage - Vérification si le vendeur a été trouvé
					print(f"Débogage - Vendeur trouvé: {vendeur_name}")
	
					# Informer le vendeur en MP de l'achat
					if vendeur:
						print(f"Envoi du message au vendeur {vendeur_name}")
						await vendeur.send(f"Bonjour {vendeur_name},\n\nL'acheteur {username} a acheté votre item **{item_name}** pour {self.currency_symbol} {price * amount} !")
						print(f"Message envoyé au vendeur {vendeur_name}")
	
					# Reverser l'argent au vendeur
					print(f"Transfert de {price * amount} au vendeur {vendeur_name}")
					await transfer_money_to_vendor(vendeur_id, price * amount)  # Appel de la fonction pour transférer l'argent
	
				except discord.NotFound:
					print(f"Erreur: Vendeur avec ID {vendeur_id} introuvable.")
				except discord.Forbidden:
					print(f"Erreur: Accès refusé pour récupérer l'utilisateur {vendeur_id}.")
				except Exception as e:
					print(f"Erreur lors de la récupération du vendeur: {e}")
	
		except Exception as e:
			print(f"Erreur dans le traitement de l'achat: {e}")
			await send_error(channel)
		return

	# ---------------------------
	#   GIVE ITEM -- can also be used to "sell"
	#				but theyll need to not fuck each other and actually pay up
	# ---------------------------

	elif command in ["give-item"]:
		"""
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		"""

		if "none" in param[1]:  # we need player pinged
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`give-item <player pinged> <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		player_ping = await get_user_id(param)

		try:
			user_fetch = bot.get_user(int(player_ping))
			print(user_fetch)
			reception_user_name = user_fetch
			print(reception_user_name)

			if int(player_ping) == user:
				# cannot send money to yourself
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Vous ne pouvez pas échanger d’objets avec vous-même. Cela serait inutile...", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		except:
			# we didnt find him
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<member>`.\n\nUsage:"
											  f"\n`give-item <player pinged> <item> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[2]:  # we need item name
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`give-item <player pinged> <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		item_name = param[2]

		if "none" in param[3]:  # we need item amount
			amount = 1
		else:
			amount = param[3]

		try:
			amount = int(amount)
			if amount < 1:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `amount`.\n\nUsage:\n`give-item <player pinged> <item short "
												  f"name> <amount>`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `amount`.\n\nUsage:\n`give-item <player pinged> <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# handler

		try:
			status, give_item_return = await db_handler.give_item(user, channel, username, user_pfp, item_name, amount, player_ping, server, message.author, reception_user_name, False) # false is for spawn_mode = False
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{give_item_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return

	# ---------------------------
	#   SPAWN ITEM
	#      if admins want to "give" someone an item without having to buy and then give it
	# ---------------------------

	elif command in ["spawn-item"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return


		if "none" in param[1]:  # we need player pinged
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`spawn-item <player pinged> <item short name> [amount]`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		player_ping = await get_user_id(param)

		try:
			user_fetch = bot.get_user(int(player_ping))
			print(user_fetch)
			reception_user_name = user_fetch
			print(reception_user_name)

		except:
			# we didnt find him
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<member>`.\n\nUsage:"
											  f"\n`spawn-item <player pinged> <item short name> [amount]`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[2]:  # we need item name
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`spawn-item <player pinged> <item short name> [amount]`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		item_name = param[2]

		if "none" in param[3]:  # we need item amount
			amount = 1
		else:
			amount = param[3]

		try:
			amount = int(amount)
			if amount < 1:
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `amount`.\n\nUsage:\n`spawn-item <player pinged> <item short name> [amount]`", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `amount`.\n\nUsage:\n`spawn-item <player pinged> <item short name> [amount]`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# handler

		try:
			status, give_item_return = await db_handler.give_item(user, channel, username, user_pfp, item_name, amount, player_ping, server, message.author, reception_user_name, True) # True is for spawn_mode = True
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{give_item_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return

	# --------------
	# 	  USE ITEM     # this will MERELY remove the item from inventory
	# --------------

	elif command in ["use", "use-item"]:  # no alias

		if "none" in param[1]:  # we need an item used
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`use-item <item short name> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		else:
			item_used = param[1]

		if "none" in param[2]:  # we need item amount
			amount_used = 1     # by default it will be 1
		else:
			amount_used = param[2]
			try:
				amount_used = int(amount_used)
			except:
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Le montant doit être un nombre entier (entier).\n\nUsage:\n`use-item <item short name> <amount>`",
					color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		try:
			status, use_return = await db_handler.use_item(user, channel, username, user_pfp, item_used, amount_used)

			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{use_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		except Exception as e:
			print(e)
			await send_error(channel)

	# ---------------------------------------
	#   CHECK INVENTORY (check own inventory)
	# ---------------------------------------

	elif command in ["inventory"]:
		# by default, you look at your own inventory.
		# this is prob useless and its easier to just put user_to_check_uname=none in the func init.py
		# but for now this will do
		user_to_check, user_to_check_uname, user_to_check_pfp = "self", "self", "self"
		# or if for another member
		if param[1] == "none":
			page_number = 1
		else:
			try:
				page_number = int(param[1])
			except:
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Numéro de page non valide.\n\nUsage:\n`inventory [page]`", color=color)
				embed.set_footer(text="info : l’utiliser sans page une fois, la sortie montrera le nombre de pages total.\ninfo : utiliser user-inventory pour voir l’inventaire d’un autre utilisateur.")
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		# handler

		try:
			status, inventory_return = await db_handler.check_inventory(user, channel, username, user_pfp, user_to_check, user_to_check_uname, user_to_check_pfp, page_number)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{inventory_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return

	# --------------------------------------------------------
	#   CHECK USER INVENTORY (check inventory of another user)
	# --------------------------------------------------------

	elif command in ["user-inventory"]:
		# by default, you look at your own inventory.
		# this is prob useless and its easier to just put user_to_check_uname=none in the func init.py
		# but for now this will do
		# or if for another member

		if "none" in param[1]:  # we need a member pinged
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`user-inventory <member> [page]`", color=color)
			embed.set_footer(text="info : utilisez ``inventory`` pour voir votre propre inventaire.")
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		else:
			# to get his id
			user_to_check = await get_user_id(param)

			try:
				# used for @-mention.

				user_to_check_uname_b = bot.get_user(int(user_to_check))
				user_to_check_uname = user_to_check_uname_b.name  # idk why we need this but without it breaks
				user_to_check_pfp = user_to_check_uname_b.display_avatar
				if int(user_to_check) == user:
					user_to_check, user_to_check_uname, user_to_check_pfp = "self", "self", "self"
			except:
				# we didnt find him
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Ping invalide.\n\nUsage:\n`user-inventory <member> [page]`", color=color)
				embed.set_footer(text="info : utilisez ``inventory`` pour voir votre propre inventaire.")
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return

		if param[2] == "none":
			page_number = 1
		else:
			try:
				page_number = int(param[2])
			except Exception as error_code:
				print(error_code)
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Numéro de page non valide.\n\nUsage:\n`user-inventory <member> [page]`", color=color)
				embed.set_footer(text="info : l’utiliser sans page une fois, la sortie montrera le nombre total de pages")
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return



		# handler

		try:
			status, inventory_return = await db_handler.check_inventory(user, channel, username, user_pfp, user_to_check, user_to_check_uname, user_to_check_pfp, page_number)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{inventory_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return

	# ---------------------------
	#   ITEMS CATALOG
	# ---------------------------

	elif command in ["catalog", "items", "item-list", "list-items", "shop"]:

		if "none" in param[1]:  # we need item name
			item_check = "default_list"
		else:
			item_check = param[1]

		# handler
		try:
			status, catalog_return = await db_handler.catalog(user, channel, username, user_pfp, item_check, server)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{catalog_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return


	# ---------------------------
	#   ADD ROLE INCOME ROLE
	# ---------------------------

	elif command in ["add-income-role", "add-role-income"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return
		
		await channel.send("Info: the income amount specified is an DAILY one.\nRemember: you need to manually update income.")
		
		if "none" in param[1] or "none" in param[2]:  # we need 3 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`add-income-role <role pinged> <income>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# check role

		income_role = await get_role_id_single(param[1])

		try:
			role = discord.utils.get(server.roles, id=int(income_role))
		except Exception as e:
			print(e)
			await channel.send(f"{emoji_error}  Rôle invalide attribué.")
			return

		# check amount
		amount = param[2]
		# they can use the thousands separator comma
		try:
			newAmount = []
			for char in amount:
				if char != ",":
					newAmount.append(char)
			amount = "".join(newAmount)
			amount = int(amount)
			if amount < 1:
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Argument donné non valide `<amount>`.\n\nUsage:\n`add-income-role <role pinged> <amount>`",
					color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Argument donné non valide `<amount>`.\n\nUsage:\n`add-income-role <role pinged> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# handler
		try:
			status, create_role_return = await db_handler.new_income_role(user, channel, username, user_pfp, income_role, amount)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{create_role_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return

	# ---------------------------
	#   REMOVE ROLE
	# ---------------------------

	elif command in ["remove-income-role", "delete-income-role", "remove-role-income", "delete-role-income"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1]:  # we need 1 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`remove-income-role <role pinged>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# check role

		income_role_beta = str(param[1])  # see another instance where i use this to see why
		income_role = ""
		for i in range(len(income_role_beta)):
			try:
				income_role += str(int(income_role_beta[i]))
			except:
				pass

		try:
			role = discord.utils.get(server.roles, id=int(income_role))
		except Exception as e:
			print(e)
			await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
			return

		# handler
		try:
			status, remove_role_return = await db_handler.remove_income_role(user, channel, username, user_pfp, income_role)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{remove_role_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

		color = discord.Color.from_rgb(102, 187, 106)  # green
		embed = discord.Embed(description=f"{emoji_worked}  Le rôle n'a pas de salaire.", color=color)
		embed.set_author(name=username, icon_url=user_pfp)
		embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
		await channel.send(embed=embed)

		return

	# ---------------------------
	#   REMOVE MONEY BY ROLE
	# ---------------------------

	elif command in ["remove-money-role", "remove-role-money"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		if "none" in param[1] or "none" in param[2]:  # we need 2 parameters
			color = discord_error_rgb_code
			embed = discord.Embed(
				description=f"{emoji_error}  Trop peu d’arguments donnés.\n\nUsage:\n`remove-money-role <role pinged> <amount>`",
				color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		amount = param[2]
		try:
			# they can use the thousands separator comma
			newAmount = []
			for char in amount:
				if char != ",":
					newAmount.append(char)
			amount = "".join(newAmount)
			amount = int(amount)
			if amount < 1:
				color = discord_error_rgb_code
				embed = discord.Embed(
					description=f"{emoji_error}  Argument donné non valide `<amount>`.\n\nUsage:\n`remove-money-role <role pinged> <amount>`",
					color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except:
			color = discord_error_rgb_code
			embed = discord.Embed(
				description=f"{emoji_error}  Argument donné non valide `<amount>`.\n\nUsage:\n`remove-money-role <role pinged> <amount>`", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		# check role

		income_role = await get_role_id_single(param[1])

		try:
			role = discord.utils.get(server.roles, id=int(income_role))
		except Exception as e:
			print(e)
			await channel.send(f"{emoji_error}  Le rôle attribué n’est pas valide. Veuillez réessayer.")
			return

		# handler
		try:
			status, remove_money_role_return = await db_handler.remove_money_role(user, channel, username, user_pfp, server, income_role, amount)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{remove_money_role_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return

	# ---------------------------
	#   LIST INCOME ROLES
	# ---------------------------

	elif command in ["list-roles", "list-income-roles", "list-role-income", "list-incomes", "list-role"]:
		try:
			status, list_roles_return = await db_handler.list_income_roles(user, channel, username, user_pfp, server)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{list_roles_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
		return

	# ---------------------------
	#   UPDATE INCOMES
	# ---------------------------

	elif command in ["update-income"]:
		if not ("Gérant Bot" in staff_request or "Gérant Bot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant Bot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		try:
			status, update_incomes_return = await db_handler.update_incomes(user, channel, username, user_pfp, server)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{update_incomes_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

		color = discord.Color.from_rgb(102, 187, 106)  # green
		embed = discord.Embed(description=f"{emoji_worked}  Les utilisateurs ayant des rôles enregistrés ont reçu leurs revenus (dans leur compte bancaire).", color=color)
		embed.set_author(name=username, icon_url=user_pfp)
		embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
		await channel.send(embed=embed)

		return


	# ---------------------------
	#   UPDATE INCOME FOR YOURSELF ONLY
	# ---------------------------

	elif command in ["collect", "get-salary", "update-income-solo"]:

		try:
			status, update_incomes_return = await db_handler.update_incomes_solo(user, channel, username, user_pfp, server, user_roles)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{update_incomes_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)

		"""
		color = discord.Color.from_rgb(102, 187, 106)  # green
		embed = discord.Embed(description=f"{emoji_worked}  You have received {update_incomes_return} for your roles {roles_return} (into bank account).", color=color)
		embed.set_author(name=username, icon_url=user_pfp)
		embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
		await channel.send(embed=embed)
		"""
		return
	
	
	# ---------------------------
	#   economy stats
	# ---------------------------

	elif command in ["stats", "economy-stats", "statistics"]:

		try:
			status, economy_stats_return = await db_handler.economy_stats(user, channel, username, user_pfp, server)
			if status == "error":
				color = discord_error_rgb_code
				embed = discord.Embed(description=f"{economy_stats_return}", color=color)
				embed.set_author(name=username, icon_url=user_pfp)
				embed.set_footer(text=f"{nom_bot} | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await channel.send(embed=embed)
				return
		except Exception as e:
			print(e)
			await send_error(channel)
			
			
		return
	
	# ---------------------------
	# START/STOP/MAINTENANCE/POST
	# ---------------------------
	
	elif command in ["start"]:
		if not ("Gérant BoukiBot" in staff_request or "Gérant BoukiBot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant BoukiBot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"BoukiBot | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		try:
			channel = bot.get_channel(channelBoukiBot)
			await channel.send("-# <@&1321073676946243616>")
			embed = discord.Embed(description=f"## {emoji_error}  BoukiBot part temporairement !",color=discord.Color.red())
			embed.add_field(name="\n🛠 Statut", value="Hors ligne", inline=True)
			embed.set_footer(text=f"BoukiBot | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
	
			await channel.send(embed=embed)
			print(f"Début de la maintenance.")
			
			channel = bot.get_channel(log_channel)
			await channel.send("Message posté")
		
		except Exception as e:
			print(e)
			await send_error(channel)
	
	
	elif command in ["stop"]:
		if not ("Gérant BoukiBot" in staff_request or "Gérant BoukiBot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant BoukiBot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"BoukiBot | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		try:
			channel = bot.get_channel(channelBoukiBot)
			await channel.send("-# <@&1321073676946243616>")
			embed = discord.Embed(description=f"## 🎉  BoukiBot est de retour !", color=discord.Color.green())
			embed.add_field(name="\n🛠 Statut", value="En ligne", inline=True)
			embed.set_footer(text=f"BoukiBot | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
	
			await channel.send(embed=embed)
			print(f"Fin de la maintenance.")
			
			channel = bot.get_channel(log_channel)
			await channel.send("Message posté")
		
		except Exception as e:
			print(e)
			await send_error(channel)
		
	elif command in ["maintenance"]:
		if not ("Gérant BoukiBot" in staff_request or "Gérant BoukiBot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant BoukiBot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"BoukiBot | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		try:
			channel = bot.get_channel(channelBoukiBot)
			await channel.send("-# <@&1321073676946243616>")
			embed=discord.Embed(description="## Maintenance de <@1318161613202653194> <t:1736272800:R>", color=discord.Color.blue())
			embed.add_field(name="", value="**Revenez ici dans quelques temps nous enverrons un message ici quand le Bot sera mis à jour.**", inline=False)
			embed.add_field(name="** **", value="Fin prévue de la maintenance : **environ le <t:1736280000:F>**", inline=False)
			embed.add_field(name="", value="-# Envie de recevoir les notifications des prochaines maintenances ?\n-# Prenez le rôle dans <#1298357497916035184> !", inline=False)
			embed.set_footer(text=f"BoukiBot | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			
			await channel.send(embed=embed)
			print(f"Annonce de la maintenance.")
			
			channel = bot.get_channel(log_channel)
			await channel.send("Message posté")
		
		except Exception as e:
			print(e)
			await send_error(channel)
		
	elif command in ["post"]:
		if not ("Gérant BoukiBot" in staff_request or "Gérant BoukiBot et Mafieux" in staff_request):
			color = discord_error_rgb_code
			embed = discord.Embed(description=f"🔒 Nécessite le rôle Gérant BoukiBot", color=color)
			embed.set_author(name=username, icon_url=user_pfp)
			embed.set_footer(text=f"BoukiBot | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			await channel.send(embed=embed)
			return

		try:
			channel = bot.get_channel(channelBoukiBot)
			await channel.send("-# <@&1321073676946243616>")
			embed=discord.Embed(description="# Mise en arrêt temporaire", color=discord.Color.blue())
			embed.add_field(name="", value="**Le Bot sera éteint aujoud'hui à partir d'environ 9h40 (<t:1737189600:R>) jusqu'a environ 12h (<t:1737198000:R>) pour cause de réunion webradio je m'en excuse d'avance.**", inline=False)
			embed.add_field(name="", value="-# Envie de recevoir les notifications des prochains posts ?\n-# Prenez le rôle dans <#1298357497916035184> !", inline=False)
			embed.set_footer(text=f"BoukiBot | {current_time}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
			
			await channel.send(embed=embed)
		
			print(f"Message posté.")
			
			channel = bot.get_channel(log_channel)
			await channel.send("Message posté.")
		
		except Exception as e:
			print(e)
			await send_error(channel)
	
	await bot.process_commands(message)

bot.run(token)
