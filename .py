import discord
import TokenDoc
import youtube_dl
import os
import csv
import re
import sys
import logging
import threading
import time
import requests
import random
import urllib
import datetime

print("Hal is online")

CREATOR_ID="653386075095695361"
HAL_ID="663923530626367509"

time_message=None
PREVIOUS_VIDEO=None
time_message=None
time_s = 0

client = discord.Client()
Player = None
Memberinfo = []
Blocked=[]
Voice=[]

today = datetime.date.today()
now = datetime.datetime.now()


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="AI Creation", type = 1, url="https://www.youtube.com/watch?v=NiUmFQY3LNA"))


@client.event
async def on_message(message):
    global Player
    global Blocked
    import datetime

    user = message.server.get_member(HAL_ID)
    channel = message.author.voice.voice_channel
    
    if str(message.content).upper() == ("*TEST"):
        em = discord.Embed(colour = 3447033)
        em.set_author(name="Test Complete")
        await client.send_message(message.channel, embed = em)

    if str(message.content).upper() == ("*LEAVE"):
         if message.author.id==CREATOR_ID:
            await client.voice_client_in(message.server).disconnect()
            em = discord.Embed(colour=3447003)
            em.set_author(name="Hal has been disconnect from the voice channel")
            await client.send_message(message.channel, embed=em)
            
    if str(message.content).upper().startswith("*PLAY|"):
        if Player!=None:
            if Player.is_playing():
                Player.stop()
        try:
            query_string = urllib.parse.urlencode({"search_query" : str(message.content).split('|')[1]})
            req = urllib.request.Request("http://www.youtube.com/results?" + query_string)
            with urllib.request.urlopen(req) as html:
                searchresults = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
                link = ("http://www.youtube.com/watch?v=" + searchresults[0])
            if message.server.get_member_named("Hal").voice.voice_channel == None:
                channel=message.author.voice.voice_channel
                await client.join_voice_channel(channel)
                Player=await message.server.voice_client.create_ytdl_player(link)
                Player.start()
                em = discord.Embed(title=" Playing: " + Player.title, description=('Duration: ')+str(int(round(Player.duration/60)))+(' Minutes \nLink: '+link), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                em.set_footer(text="Hal | {:%b,%d %Y}".format(today))
                await client.send_message(message.channel, embed=em)
            else:
                channel=message.author.voice.voice_channel
                try:
                    Player=await message.server.voice_client.create_ytdl_player(link)
                except:
                    channel=message.author.voice.voice_channel
                    await client.join_voice_channel(channel)
                    Player=await message.server.voice_client.create_ytdl_player(link)
                Player.start()
                em = discord.Embed(title=" Playing: " + Player.title, description=('Duration: ')+str(int(round(Player.duration/60)))+(' Minutes \nLink: '+link), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await client.send_message(message.channel, embed=em)
        except IndexError:
            await client.send_message(message.channel, ("Could not find this video on YouTube."))


   
client.loop.run_until_complete(client.start(TokenDoc.token))


