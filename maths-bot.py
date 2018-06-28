#https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord

TOKEN = 'XXX'
WEEKLY_URL = "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/weekly-maths-challenge.aspx"

#Function to get the current weekly challenge Title and Description
def weekly():
    import requests
    from bs4 import BeautifulSoup

    #Gets the entire webpage HTML
    r = requests.get(WEEKLY_URL)
    html = r.text

    #the Title is always 2 'siblings' after the first h3 tag
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.h3.next_sibling.next_sibling

    text = ""
    element = title
    #The description is a variable length, but always ends with an <hr/> tag.
    #This loops until that tag is reached, adding the text (that isn't blank, there is a lot of whitespace) to the Decription
    while "<hr/>" not in str(element):
        element = element.next_sibling
        #print(element)
        if (str(element).rstrip()) != "":
            text += element.getText()
        else:
            text += "\n"

    message = "**"+title.getText()+"**\n"+text #Returns the message for the bot to send; the Title in bold and the challenge description after it
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