import random, discord, time, asyncio, datetime
from babel.dates import format_datetime
from config import *

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
        embed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')} | ÇA TOURNE ! ... Temps restant: 10 secondes", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
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
