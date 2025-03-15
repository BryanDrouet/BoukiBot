import random, discord, datetime
from babel.dates import format_datetime
from config import *

class Card:
	def __init__(self, rank, suit):
		self.rank = rank
		self.suit = suit
		self.cardName = {1: 'As', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'Valet', 12: 'Dame', 13: 'Roi'}
		self.cardSuit = {'c': 'Trèfle', 'h': 'Cœur', 's': 'Pique', 'd': 'Carreau'}

	def __str__(self):
		return (self.cardName[self.rank] + " de " + self.cardSuit[self.suit])

	def getRank(self):
		return (self.rank)

	def getSuit(self):
		return (self.suit)

	def BJValue(self):
		if self.rank > 9:
			return (10)
		else:
			return (self.rank)

class blackjack_discord_implementation:
	def __init__(self, bot, channel, currency_symbol):
		self.currency_symbol = currency_symbol
		self.bot = bot
		self.channel = channel
		self.loopCount = -1
		self.cardName = {1: 'As', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'Valet', 12: 'Dame', 13: 'Roi'}
		self.cardSuit = {'c': 'Trèfle', 'h': 'Cœur', 's': 'Pique', 'd': 'Carreau'}

	def handCount(self, hand):
		handCount = 0
		for card in hand:
			handCount += card.BJValue()
		return (handCount)

	async def get_user_input(self, message):
		answer = await self.bot.wait_for("message", check=lambda response: response.author == message.author)
		answer = answer.content
		answer = answer.lower().strip()
		if answer not in ["hit", "stand"]:
			return "none"

		return answer

	async def play(self, bot, channel, username, user_pfp, message, bet):
		self.bot = bot
		deck = []
		suits = ['c', 'h', 'd', 's']
		score = {'computer': 0, 'human': 0}
		hand = {'computer': [], 'human': []}

		for suit in suits:
			for rank in range(1, 14):
				deck.append(Card(rank, suit))

		keepPlaying = True

		while keepPlaying:
			random.shuffle(deck)
			random.shuffle(deck)
			random.shuffle(deck)

			hand['human'].append(deck.pop(0))
			hand['computer'].append(deck.pop(0))

			hand['human'].append(deck.pop(0))
			hand['computer'].append(deck.pop(0))

			playHuman = True
			bustedHuman = False

			while playHuman:
				self.loopCount += 1

				if self.loopCount == 0:
					color = discord.Color.from_rgb(3, 169, 244)
					firstEmbed = discord.Embed(description=f"Ecrit `hit` pour piocher une carte, ou `stand` pour passer.", color=color)
					firstEmbed.set_author(name=username, icon_url=user_pfp)
					firstEmbed.add_field(name="**Votre main**", value=f"X X\nValeur {self.handCount(hand['human'])}", inline=True)
					firstEmbed.add_field(name="**Le croupier vous montre**", value=f"{str(hand['computer'][-1])}\nValeur ?", inline=True)
					firstEmbed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					sentFirstEmbed = await channel.send(embed=firstEmbed)
				else:
					
					color = discord.Color.from_rgb(3, 169, 244)
					newEmbed = discord.Embed(description=f"Ecrit `hit` pour piocher une carte, ou `stand` pour passer.", color=color)
					newEmbed.set_author(name=username, icon_url=user_pfp)
					newEmbed.add_field(name="**Votre main**", value=f"X X\nValeur {self.handCount(hand['human'])}", inline=True)
					newEmbed.add_field(name="**Le croupier vous montre**", value=f"{str(hand['computer'][-1])}\nValeur ?", inline=True)
					firstEmbed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
					await sentFirstEmbed.edit(embed=newEmbed)


				if self.handCount(hand['human']) == 21:
					playHuman = False
					break
				
				inputCycle = True
				userInput = ''
				
				while inputCycle:
					userInput = await self.get_user_input(message)
					if userInput != "none": inputCycle = False


				if userInput == 'hit':
					hand['human'].append(deck.pop(0))
					if self.handCount(hand['human']) > 21:
						playHuman = False
						bustedHuman = True
				elif userInput == 'stand':
					playHuman = False

			playComputer = True
			bustedComputer = False

			while not bustedHuman and playComputer:
				
				if self.handCount(hand['computer']) < 17:
					hand['computer'].append(deck.pop(0))
				else:
					playComputer = False

				if self.handCount(hand['computer']) > 21:
					playComputer = False
					bustedComputer = True

			print("pc : ", self.handCount(hand['computer']), "player : ", self.handCount(hand['human']))

			if self.handCount(hand['human']) == 21:
				color = discord.Color.from_rgb(102, 187, 106)
				pcBustedEmbed = discord.Embed(description=f"Resultat : blackjack! {str(self.currency_symbol)} +{'{:,}'.format(bet*1.5)}", color=color)
				pcBustedEmbed.set_author(name=username, icon_url=user_pfp)
				pcBustedEmbed.add_field(name="**Votre main**", value=f"X X\nValeur {self.handCount(hand['human'])}", inline=True)
				pcBustedEmbed.add_field(name="**Le croupier vous montre**", value=f"X X\nValeur {self.handCount(hand['computer'])}", inline=True)
				pcBustedEmbed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await sentFirstEmbed.edit(embed=pcBustedEmbed)

				return "blackjack"

			elif bustedHuman:
				color = discord.Color.from_rgb(239, 83, 80)
				playerBustEmbed = discord.Embed(description=f"Resultat : Bust {str(self.currency_symbol)} -{'{:,}'.format(bet)}", color=color)
				playerBustEmbed.set_author(name=username, icon_url=user_pfp)
				playerBustEmbed.add_field(name="**Votre main**", value=f"X X\nValeur {self.handCount(hand['human'])}", inline=True)
				playerBustEmbed.add_field(name="**Le croupier vous montre**", value=f"{str(hand['computer'][-1])}\nValeur ?", inline=True)
				playerBustEmbed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await sentFirstEmbed.edit(embed=playerBustEmbed)

				return "loss"

			elif bustedComputer:
				color = discord.Color.from_rgb(102, 187, 106)
				pcBustedEmbed = discord.Embed(description=f"Résultat : Dealer Bust {str(self.currency_symbol)} +{'{:,}'.format(bet)}", color=color)
				pcBustedEmbed.set_author(name=username, icon_url=user_pfp)
				pcBustedEmbed.add_field(name="**Votre main**", value=f"X X\nValeur {self.handCount(hand['human'])}", inline=True)
				pcBustedEmbed.add_field(name="**Le croupier vous montre**", value=f"X X\nValeur {self.handCount(hand['computer'])}", inline=True)
				pcBustedEmbed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await sentFirstEmbed.edit(embed=pcBustedEmbed)

				return "win"

			elif self.handCount(hand['human']) > self.handCount(hand['computer']):
				color = discord.Color.from_rgb(102, 187, 106)
				playerWinEmbed = discord.Embed(description=f"Résultat : Win {str(self.currency_symbol)} +{'{:,}'.format(bet)}", color=color)
				playerWinEmbed.set_author(name=username, icon_url=user_pfp)
				playerWinEmbed.add_field(name="**Votre main**", value=f"X X\nValeur {self.handCount(hand['human'])}", inline=True)
				playerWinEmbed.add_field(name="**Le croupier vous montre**", value=f"X X\nValeur {self.handCount(hand['computer'])}", inline=True)
				playerWinEmbed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await sentFirstEmbed.edit(embed=playerWinEmbed)

				return "win"

			elif self.handCount(hand['human']) == self.handCount(hand['computer']):
				color = discord.Color.from_rgb(255, 141, 1)
				playerWinEmbed = discord.Embed(description=f"Resultat : Push, money back", color=color)
				playerWinEmbed.set_author(name=username, icon_url=user_pfp)
				playerWinEmbed.add_field(name="**Votre main**", value=f"X X\nValeur {self.handCount(hand['human'])}", inline=True)
				playerWinEmbed.add_field(name="**Le croupier vous montre**", value=f"X X\nValeur {self.handCount(hand['computer'])}", inline=True)
				playerWinEmbed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await sentFirstEmbed.edit(embed=playerWinEmbed)

				return "bust"

			else:
				color = discord.Color.from_rgb(239, 83, 80)
				pcWinEmbed = discord.Embed(description=f"Resultat : Loss {str(self.currency_symbol)} -{'{:,}'.format(bet)}", color=color)
				pcWinEmbed.set_author(name=username, icon_url=user_pfp)
				pcWinEmbed.add_field(name="**Votre main**", value=f"X X\nValeur {self.handCount(hand['human'])}", inline=True)
				pcWinEmbed.add_field(name="**Le croupier vous montre**", value=f"X X\nValeur {self.handCount(hand['computer'])}", inline=True)
				pcWinEmbed.set_footer(text=f"{nom_bot} | {format_datetime(datetime.datetime.now(), format='d MMMM y à HH:mm', locale='fr_FR')}", icon_url="https://media.discordapp.net/attachments/707868018708840508/1318353739559469207/883486e0d1166d661ba2d179d0e90f99.png?ex=67620419&is=6760b299&hm=745dd8b6dab2c994d24c4a8042e12318aea7a3e94db6a956be81e16394f01249&=&format=webp&quality=lossless&width=584&height=584")
				await sentFirstEmbed.edit(embed=pcWinEmbed)

				return "loss"

		return
