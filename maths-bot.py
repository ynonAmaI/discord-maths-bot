#https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
#Import libraries
import discord
import requests
from bs4 import BeautifulSoup
from random import randint

TOKEN = 'XXX'
WEEKLY_URL = "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/weekly-maths-challenge.aspx" #All problems are sourced from the Kings Maths School Seven Day Maths website
NOTIF_CHANNEL_ID = 'XXX'
TARGET_CHANNEL_ID = 'XXX'

#Function to generate an array of all the (absolute) links to each problem.
#Currently does only problems 101 onwards, as the rest are stored differently.
#Due to how requests_html seems to work, the links seem to be placed in the list in a random order each time.
def getLinks():
        import requests_html
        session = requests_html.HTMLSession()
        r = session.get(WEEKLY_URL) #Gets the HTML of the specified URL
        links = r.html.absolute_links #Gets every absolute link found on the page...
        links = list(links) #...and then converts from a Set to a List.

        #Filters the list to only the links to a problem page.
        i = 0
        while i < len(links):
            if "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/problems/wmc" not in links[i]:
                links.remove(links[i])
            else:
                i += 1

        return links #Returns the list

#Function to get the Title of the problem from a given URL. Returns a string
def title(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.h3.next_sibling.next_sibling
    return title.getText()

#Function to get the Description of the problem from a given URL. Returns a string
def description(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    text = ""
    element = soup.h3.next_sibling.next_sibling #Description always starts after the Title, which occurs 2 'siblings' after the first h3 tag
    #The description is a variable length, but always ends with an <hr/> tag.
    #This loops until that tag is reached, adding the text (that isn't Null, or blank as there seems to be a lot of whitespace) to the Decription
    while "<hr/>" not in str(element):
        element = element.next_sibling
        if (str(element).rstrip()) != "" and element != None:
            text += element.getText()
        else:
            text += "\n"

    return text

#Function to return the message the bot should send, containing the problem's Title and Description.
#If random = False then it returns the weekly challenge, otherwise returns a random problem from the currently supported archive.
def question(random):
    #Array of all the links to problems
    links = getLinks()
    titleVar = ""
    descriptionVar = ""

    if not random: #Gets the Title and Description of the weekly challenge
        titleVar = title(WEEKLY_URL)
        descriptionVar = description(WEEKLY_URL)
    else:
        rand = randint(0, len(links)-1) #Generates a random number...
        titleVar = title(links[rand]) #...and gets the Title...
        descriptionVar = description(links[rand]) #and Description of the challenge from the link found at that index.

    message = "**"+titleVar+"**\n"+descriptionVar #Returns the message for the bot to send; the Title in bold and the challenge description after it
    return message


client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith("?weekly"): #Sends message with current weekly challenge
        msg = question(False)
        await client.send_message(message.channel, msg)

    if message.content.startswith("?question"): #Sends message with a random problem from the currently supported archive.
        msg = question(True)
        await client.send_message(message.channel, msg)

    #The bot posts a message when the weekly challenge updates; this relies on a webhook connected to their Twitter account. (which only tweets when the challenge updates)
    #The bot listens to a specific channel; this should be a private channel only used for the webhook
    #When a message is sent to the notification channel, the bot posts the weekly challenge to the target channel.
    notifChannel = client.get_channel(NOTIF_CHANNEL_ID)
    targetChannel = client.get_channel(TARGET_CHANNEL_ID)
    if message.channel == notifChannel:
        msg = "This week's challenge!\n--------------------------\n"
        msg += question(False)
        await client.send_message(targetChannel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)