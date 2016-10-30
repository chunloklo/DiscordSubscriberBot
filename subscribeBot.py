import discord
import logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

async def readFile(filename, message):
	lines = ""
	try:
		f = open(filename, "r")
		lines = f.readlines()
	except:
		await client.send_message(message.channel, "File not found. Creating new file")
		f = open(filename, "w")
	finally:
		f.close()
	return lines

async def writeFile(filename, data):
	f = open(filename, "w")
	for lines in data:
		for line in lines:
			f.write(line + " ")
		f.write("\n")
	f.close()

async def printGames(data, message):
	listofGames = []
	for lines in data:
		try:
			listofGames.append(lines[0])
		except:
			pass
	if len(listofGames) == 0:
		await printNoGames(message);
		return
	await client.send_message(message.channel, "Current list of games: " + str(listofGames))

async def parceData(rawData):
	pData = []
	#parse data
	for (val, lines) in enumerate(rawData):
		sLines = lines.split()
		pData.append([])
		for block in sLines:
			pData[val].append(block)
	return pData

async def printNoGames(message):
	await client.send_message(message.channel, "```There are no games in the database```")

client = discord.Client()

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if message.channel.id == "INSERT YOUR OWN CHATBOT'S CLIENT ID":
		if message.content.startswith("!quit"):
			msg = "Bye bye!"
			await client.send_message(message.channel, msg)
			await client.logout()


		#subscribe to game channel
		if message.content.startswith("!subscribe"):
			msg = "working on it!"
			await client.send_message(message.channel, msg)
			input = message.content.split()
			if len(input) != 2:
				await client.send_message(message.channel, "!subscribe Game")
				return;
			data = await readFile("SubscriberList.txt", message)

			#parse data
			pData = await parceData(data)

			absent = True
			for (val, lines) in enumerate(pData):
				if lines[0].lower() == input[1].lower():
					if lines.count(message.author.id) == 0:
							lines.append(message.author.id)
							await client.send_message(message.channel, "<@{0}> is now subscribed to {1}".format(message.author.id, input[1]))
					else:
						await client.send_message(message.channel, "already subscribed")
					absent = False
					break
			if absent == True:
				await printGames(pData, message)
				await client.send_message(message.channel, "<@{1}> Do you want to add this game ('{0}') and subscribe? (y or n)".format(input[1], message.author.id))
				reply = await client.wait_for_message(author=message.author)
				if reply.content == "y":
					pData.append([input[1]])
					pData[len(pData) - 1].append(message.author.id)
					await client.send_message(message.channel, "Creating {0}".format(input[1]))
				else:
					await client.send_message(message.channel, "ok")

			#write data to file
			await writeFile("SubscriberList.txt", pData)
			await client.send_message(message.channel, "Finished!")

		#unsubscribe from channel
		if message.content.startswith("!unsubscribe"):
			msg = "working on it!"
			await client.send_message(message.channel, msg)
			input = message.content.split()
			if len(input) != 2:
				await client.send_message(message.channel, "!unsubscribe Game")
			data = await readFile("SubscriberList.txt", message)
			pData = await parceData(data)
			if len(pData) == 0:
				await printNoGames(message);
				return
			absent = True
			for (val, lines) in enumerate(pData):
				if lines[0].lower() == input[1].lower():
					if lines.count(message.author.id) == 1:
							lines.remove(message.author.id)

							if len(lines) == 1:
								del  pData[val]
							msg = "<@" + message.author.id + "> is now unsubscibed from {0}".format(input[1])
							await client.send_message(message.channel, msg)
					else:
						await client.send_message(message.channel, "already unsubscribed")
					absent = False
					break
			if absent == True:
				msg = "Game does not exist"
				await client.send_message(message.channel, msg)
			#write data to file
			await writeFile("SubscriberList.txt", pData)



		#print Everything in list !database
		if message.content.startswith("!database"):
			data = await readFile("SubscriberList.txt", message)
			pData = await parceData(data)
			table = ""
			for lines in pData:
				table += ("```" + str(lines[0]) + "```")
				for players in lines[1:]:
					name = discord.utils.get(message.server.members, id=players).name
					table += (" " + name)
				# table += "\n"
			if len(table) == 0:
				await printNoGames(message);
				return
			await client.send_message(message.channel, table)

		if message.content.startswith("!call"):
			input = message.content.split()
			if len(input) <= 1:
				await client.send_message(message.channel, "!call Game message")
			data = await readFile("SubscriberList.txt", message)
			pData = await parceData(data)
			if len(pData) == 0:
				await printNoGames(message);
				return
			msg = ""
			absent = True
			for callList in pData:
				callGame = callList[0]
				if callGame.lower() == input[1].lower():
					msg += (callGame + " :\n")
					for person in callList[1:]:
						msg += "<@{0}> \n".format(person)
						absent = False
					break
			if absent == True:
				await client.send_message(message.channel, "Game you were looking for does not exist")
				return
			if len(input) >= 3:
				tempS = "```css\n"
				for words in input[2:]:
					tempS += str(words + " ")
				tempS += "\n```"
				msg = tempS + msg

			await client.send_message(message.channel, msg)

		if message.content.startswith("!help"):
			msg = "```Command List:\n!subscribe \n!unsubscribe \n!call \n!database \n!clear \n!quit```"
			await client.send_message(message.channel, msg)

		if message.content.startswith("!clear"):
			await client.send_message(message.channel, "<@{}> Are you sure you want to clear the database (y or n)".format(message.author.id))
			reply = await client.wait_for_message(author=message.author)
			if reply.content == "y":
				await client.send_message(message.channel, "If you really say so!")
				await writeFile("SubscriberList.txt", "");
			else:
				await client.send_message(message.channel, "Smart Choice")



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run("INSERT YOUR BOT'S TOKEN")