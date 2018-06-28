#https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord

TOKEN = 'XXX'
WEEKLY_URL = "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/weekly-maths-challenge.aspx"

def weekly():
    import requests
    from bs4 import BeautifulSoup

    r = requests.get(WEEKLY_URL)
    html = r.text

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.h3.next_sibling.next_sibling

    text = ""
    element = title
    while "<hr/>" not in str(element):
        element = element.next_sibling
        #print(element)
        if (str(element).rstrip()) != "":
            text += element.getText()
        else:
            text += "\n"

    message = "**"+title.getText()+"**\n"+text
    return message

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith("!weekly"):
        msg = weekly()
        await client.send_message(message.channel, msg)

    if message.content.startswith("!question"):
        #Random question from archive

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)