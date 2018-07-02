#https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
#Import libraries
import discord
import requests
from bs4 import BeautifulSoup
from random import randint
import re
import math

WEEKLY_URL = "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/weekly-maths-challenge.aspx" #All problems are sourced from the Kings Maths School Seven Day Maths website
#Problems 101 onwards have their own pages, linked from the weekly URL
ARCHIVE_URLS = ["https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/previouschallenges.aspx", "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/recentchallenges.aspx", "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/challenges-41-60.aspx", "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/challenges-61-80.aspx", "https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/challenges-81-100.aspx"]
WEEKLY_TEXT = "This week's challenge!\n--------------------------\n" #Beginning of the message that gets posted when the weekly problem updates
TOKEN = "XXX"
NOTIF_CHANNEL_ID = 'XXX'
TARGET_CHANNEL_ID = 'XXX'

#Function to generate an array of all the (absolute) links to each problem.
#Used only for problems 101 onwards, as the rest are stored differently. Urls are in ARCHIVE_URLS
#Due to how requests_html seems to work, the links seem to be placed in the list in a random order each time
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

#Used to determine when the problem description has ended. Includes every possible text signalling the description has finished, as of 02/07/2018
def endOfProblem(element):
    result = True
    if ("view the solution" in str(element).lower()):
        result = False

    if ("view the solutions" in str(element).lower()):
        result = False

    if ("view solution" in str(element).lower()):
        result = False

    if ("think you can solve it" in str(element).lower()):
        result = False

    if ("think you have the answer" in str(element).lower()):
        result = False

    if ("view the solution attempts" in str(element).lower()):
        result = False

    if ("an alternative solution was submitted" in str(element).lower()):
        result = False

    return result

#Function to get the Title of the problem from a given URL. Returns a string
#archiveNum is optional, used if the problem is before #101
def title(url, archiveNum=0):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    if url not in ARCHIVE_URLS: #If the problem has its own webpage; ie. problems 101 onwards
        title = soup.h3.next_sibling.next_sibling
    else:
        anchors = soup.find_all(class_="sys_trigger", string=re.compile("Weekly")) #Gets all title tags on the page
        archiveNum  = abs(archiveNum-20) + 19 #Because they are found in reverse order, archiveNum must be adjusted
        title = anchors[archiveNum % 20] #Modulo is used because challenges are split into groups of 20
    return title.getText()

#Function to get the Description of the problem from a given URL. Returns a string
def description(url, archiveNum=-1):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    text = ""
    if url not in ARCHIVE_URLS: #If the problem has its own webpage; ie. problems 101 onwards
        element = soup.h3.next_sibling.next_sibling #Description always starts after the Title, which occurs 2 'siblings' after the first h3 tag
        #The description is a variable length, but always ends with an <hr/> tag.
        #This loops until that tag is reached, adding the text (that isn't Null, or blank as there seems to be a lot of whitespace) to the Decription
        while "<hr/>" not in str(element):
            element = element.next_sibling
            if (str(element).rstrip()) != "" and element != None:
                text += element.getText()
            else:
                text += "\n"
    else:
        anchors = soup.find_all(class_="sys_trigger", string=re.compile("Weekly")) #Gets all title tags
        archiveNum  = abs(archiveNum-20) + 19 #Because they are found in reverse order, archiveNum must be adjusted
        elements = anchors[archiveNum % 20].next_sibling.contents #Description is nested below the next tag ('sibling') from the title. Modulo is used because challenges are split into groups of 20.
        j = 0
         #This loops until the problem description has ended, adding the text (that isn't Null, or blank as there seems to be a lot of whitespace) to the Decription
        while endOfProblem(elements[j]) and j != len(elements)-1:
            if (str(elements[j]).rstrip()) != "" and elements[j] != None:
                text += elements[j].getText()
            else:
                text += "\n"
            j += 1
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
        #1 less than len(links) for all problems with their own page, +100 for all other archived problems.
        rand = randint(0, len(links)-1+100) #Generates a random number...
        if rand >= 100: #(ie. problem has its own webpage)
            titleVar = title(links[rand-100]) #...and gets the Title...
            descriptionVar = description(links[rand-100]) #and Description of the challenge from the link found at that index.

        else:
            #...gets the title and description for that problem. math.floor(rand / 20) is to get the correct group and URL
            titleVar = title(ARCHIVE_URLS[math.floor(rand / 20)], rand) 
            descriptionVar = description(ARCHIVE_URLS[math.floor(rand / 20)], rand)
    message = "**"+titleVar+"**\n"+descriptionVar #Returns the message for the bot to send; the Title in bold and the challenge description after it
    return message

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith("!weekly"): #Sends message with current weekly challenge
        msg = question(False)
        await client.send_message(message.channel, msg)

    if message.content.startswith("!question"): #Sends message with a random problem from the currently supported archive.
        msg = question(True)
        await client.send_message(message.channel, msg)
        

    #The bot posts a message when the weekly challenge updates; this relies on a webhook connected to their Twitter account. (which only tweets when the challenge updates)
    #The bot listens to a specific channel; this should be a private channel only used for the webhook
    #When a message is sent to the notification channel, the bot posts the weekly challenge to the target channel.
    notifChannel = client.get_channel(NOTIF_CHANNEL_ID)
    targetChannel = client.get_channel(TARGET_CHANNEL_ID)
    if message.channel == notifChannel and message.content.startswith("!post"):
        msg = WEEKLY_TEXT
        msg += question(False)

        currentPins = await client.pins_from(targetChannel) #Gets all current pins from the channel where the message is to be posted
        for i in currentPins: #Loops through all currently pinned messages
            if i.content.startswith(WEEKLY_TEXT) and i.author == client.user: #If the message is the last weekly problem post
                await client.unpin_message(i) #Unpin the message

        toPin = await client.send_message(targetChannel, msg) #Sends the message to the target channel, and assigns that message to the variable toPin
        await client.pin_message(toPin) #Pins the message

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)