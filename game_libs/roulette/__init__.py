import random, discord, time, datetime, sys, os ,logging
from babel.dates import format_datetime
from config import *

sys.stdout.reconfigure(encoding='utf-8')
logger = logging.getLogger(f"{nom_bot}")
logger.setLevel(logging.INFO)
if not logger.handlers:
	handler = logging.StreamHandler(sys.stdout)
	handler.setFormatter(logging.Formatter('%(message)s'))
	logger.addHandler(handler)

os.makedirs("cache", exist_ok=True)
log_filename = datetime.datetime.now().strftime("cache/logs_%Y-%m-%d_%H-%M-%S.txt")
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(levelname)s  |  %(asctime)s\n%(message)s\n\n'))
logger = logging.getLogger(nom_bot)  # ou "discord_bot", selon ton code
logger.setLevel(logging.INFO)
if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
    logger.addHandler(file_handler)
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.INFO)
if not any(isinstance(h, logging.FileHandler) for h in discord_logger.handlers):
    discord_logger.addHandler(file_handler)
gateway_logger = logging.getLogger('discord.gateway')
gateway_logger.setLevel(logging.INFO)
if not any(isinstance(h, logging.FileHandler) for h in gateway_logger.handlers):
    gateway_logger.addHandler(file_handler)

class roulette_discord_implementation:
    def __init__(self, bot, channel, currency_emoji):
        self.bot = bot
        self.channel = channel
        self.currency_symbol = currency_emoji
        self.slots = {'0': 'green', '1': 'rouge', '2': 'noir',
                      '3': 'rouge', '4': 'noir', '5': 'rouge', '6': 'noir', '7': 'rouge',
                      '8': 'noir', '9': 'rouge', '10': 'noir', '11': 'rouge',
                      '12': 'noir', '13': 'rouge', '14': 'noir', '15': 'rouge',
                      '16': 'noir', '17': 'rouge', '18': 'noir', '19': 'rouge',
                      '20': 'noir', '21': 'rouge', '22': 'noir', '23': 'rouge',
                      '24': 'noir', '25': 'rouge', '26': 'noir', '27': 'rouge',
                      '28': 'noir', '29': 'rouge', '30': 'noir', '31': 'rouge',
                      '32': 'noir', '33': 'rouge', '34': 'noir', '35': 'rouge',
                      '36': 'noir'}

    """
    Pas utilisé pour l'instant, mais peut-être utile si on veut permettre à plusieurs joueurs de jouer à la roulette en même temps.

    async def get_user_input(self, message):
        # On attend une réponse de la personne qui souhaite jouer
        answer = await self.bot.wait_for("message", check=lambda response: response.author == message.author)
        answer = answer.content
        # Nettoyer la réponse
        answer = answer.lower().strip()
        # On veut seulement "hit" ou "stand", rien d'autre
        if answer not in ["hit", "stand"]:
            return "none"
        return answer
    """

    async def play(self, bot, channel, username, user_pfp, bet, space, mention):
        self.bot = bot
        
        spaceType = "string"
        try:
            space = int(space)
            spaceType = "int"
        except:
            pass
        space = str(space).lower().strip()

        color = discord.Color.from_rgb(3, 169, 244)
        embed = discord.Embed(description=f"Tu mises {str(self.currency_symbol)} {bet} sur `{space}`.", color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        embed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')} | ÇA TOURNE ! ... Temps restant: 10 secondes", icon_url=BOT_ICON)
        await channel.send(embed=embed)

        time.sleep(10)

        win = lose = multiplicator = None

        if space in ["odd", "even", "noir", "rouge"]:
            multiplicator = 2
        else:
            multiplicator = 35

        result = random.choice(list(self.slots.keys()))
        result_prompt = f"La balle à attéri sur **{result} {self.slots[result]}** !\n\n"

        if space == "noir" or space == "even": 
            result = int(result)
            win = 1 if (result % 2) == 0 else 0

        elif space == "rouge" or space == "odd":
            result = int(result)
            win = 1 if (result % 2) != 0 else 0

        elif spaceType == "int":
            win = 1 if space == result else 0

        else:
            print("erreur")

        if win:
            result_prompt += f"🎉  **CHAMPIOOONS**  🎉\n{mention} a gagné {str(self.currency_symbol)} {bet*multiplicator}\n-# {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}"
        else:
            result_prompt += f"**Pas de gagnant :(**\n-# {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}"

        await channel.send(result_prompt)

        return win, multiplicator
