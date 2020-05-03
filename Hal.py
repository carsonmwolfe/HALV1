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
import asyncio

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


ytdl_format_options = {
    'format': 'bestaudio/best',
    'download': False
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self,source,*,data,volume=1.0):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.duration = data.get('duration')
        self.is_live = False

    @classmethod
    async def from_url(cls,url,*,loop=None,stream=False):
        loop = loop
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download = not stream))
        cls.url = url

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data = data)
    



today = datetime.date.today()
now = datetime.datetime.now()


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Rewrite is superior", type = 1, url="https://www.youtube.com/watch?v=NiUmFQY3LNA"))


@client.event
async def on_message(message):
    global Player
    global Blocked
    import datetime

    user = message.guild.get_member(HAL_ID)
    channel = message.author.voice.channel
    
    
    if str(message.content).upper() == ("*TEST"):
        em = discord.Embed(colour = 3447033)
        em.set_author(name="Test Complete")
        await client.send(message.channel, embed = em)

    if str(message.content).upper() == ("*LEAVE"):
         if message.author.id==CREATOR_ID:
            await client.voice_client_in(message.guild).disconnect()
            em = discord.Embed(colour=3447003)
            em.set_author(name="Hal has been disconnect from the voice channel")
            await client.send(message.channel, embed=em)

    if str(message.content).upper().upper()==("*MOVE"):
        if message.author.id!=CREATOR_ID:
            em = discord.Embed(colour=3447003)
            em.set_author(name = "This Command Is A CREATOR ONLYCommand")
            await client.send(message.channel, embed=em)
        if message.author.id==CREATOR_ID:
            await client.move_member(user,channel)
            em = discord.Embed(colour=3447003)
            em.set_author(name = "Hal Has moved channels" + "\n" + "Note: If Hal Moves During A Song, The Song Will Stop Playing ")
            await client.send(message.channel, embed=em)

    if str(message.content).upper().startswith("*VOLUME|"):
        Player.volume
        total= int(str(message.content).split('|')[1])
        Player.volume=total/100
        em = discord.Embed(colour=3447003)
        em.set_author(name="Music Volume has been changed to {0}".format(str(total))+"%." )
            
     
    if str(message.content).upper().startswith("*PLAY|"):
        
        if Player!=None:
            if is_playing():
                Player.stop()
        try:
            query_string = urllib.parse.urlencode({"search_query" : str(message.content).split('|')[1]})
            req = urllib.request.Request("http://www.youtube.com/results?" + query_string)
            with urllib.request.urlopen(req) as html:
                searchresults = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
                link = ("http://www.youtube.com/watch?v=" + searchresults[0])        
            if message.guild.voice_client == None:
                channel=message.author.voice.channel
                await channel.connect()
                Player = await YTDLSource.from_url(link,loop = asyncio.get_event_loop())
                await message.guild.voice_client.play(Player)
                em = discord.Embed(title=" Playing: " + Player.title, description=('Volume:  {0}'.format(str(Player.volume*100))+"%." + 'Duration: '+str(int(round(Player.duration/60)))+(' Minutes \nLink: '+ link)), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                em.set_footer(text="Hal | {:%b,%d %Y}".format(today))
                await client.send(message.channel, embed=em)
            else:
                channel=message.author.voice.channel
                try:
                    Player = await YTDLSource.from_url(link,loop = asyncio.get_event_loop())
                except:
                    channel=message.author.voice.channel
                    await channel.connect()
                    Player = await YTDLSource.from_url(link,loop = asyncio.get_event_loop())
                await message.guild.voice_client.play(Player)
                em = discord.Embed(title=" Playing: " + Player.title, description=('Volume:  {0}'.format(int(Player.volume*100))+"%." + "\n" + 'Duration: '+str(int(round(Player.duration/60)))+(' Minutes \nLink: '+ link)), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await client.send(message.channel, embed=em)
        except IndexError:
            await message.channel.send ("Could not find this video on YouTube.")
            if(player.is_playing == False):
                em= discord.Embed(description = Player.title +link+ "\n" + "**Song Has Ended**", colour = 3447003)
                em.set_author(name = "Music", icon_url=message.author.avatar_url)
                await client.send(message.channel, embed=em)
                                  


   
client.loop.run_until_complete(client.start(TokenDoc.token))


