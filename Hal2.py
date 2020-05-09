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

print("Hal is Booting up...")

#uration_in_s = duration.total_seconds()
#days = divmod(duration_in_s, 86400)
#hours = divmod(days[1],3600)
#minutes = divmod(hour[1], 60)
#seconds = divmod(minutes[1], 1)

Startup = datetime.datetime.now()


CREATOR_ID=653386075095695361
HAL_ID=663923530626367509

time_message=None
PREVIOUS_VIDEO=None
time_message=None
time_s = 0

client = discord.Client()
Player = None
Memberinfo = []
Blocked=[]
Voice=[]
profooter=""
EMBEDCOLOR = 3447033
DARK_NAVY = 2899536



ytdl_format_options = {
    'format': 'bestaudio/best',
    'download': False
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'options': '-vn'
}
      
        
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(MS,source,*,data,volume=1.0):
        super().__init__(source, volume)

        MS.data = data
        MS.title = data.get('title')
        MS.duration = data.get('duration')
        MS.is_live = False
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
    global MusicAuthorID
    global Blocked
    global Volume
    global MusicMSG
    global Execute_Order_66
    Volume = 1.0
    import datetime
    user = message.guild.get_member(HAL_ID)
    channel = message.author.voice.channel
    if str(message.content).upper() == ("*TEST"):
        em = discord.Embed(colour = 3447033)
        em.set_author(name="Test Complete")
        await message.channel.send(embed = em)

    if str(message.content).upper() == ("*LEAVE"):
        await message.guild.voice_client.disconnect()
        em = discord.Embed(colour=3447003)
        em.set_author(name="Hal has been disconnect from the voice channel")
        Player = None
        await message.channel.send(embed=em)

    if str(message.content).upper() == ("*RESTART"):
        if message.author.id!=CREATOR_ID:
            em = discord.Embed(colour=3447003)
            em.set_author(name="This Command Is A Creator Only Command.")
            await client.send_message(message.channel, embed=em)

        if message.author.id==CREATOR_ID:
            client.loop.run_until_complete(client.logout())
            os.system("python3 /home/pi/Hal.py")
            #os.system("C:\Users\cmwol\Desktop\__pycache__\python\HAL")
            raise SystemExit
            

    if str(message.content).upper().upper()==("*MOVE"):
        await user.edit(voice_channel = channel)
        em = discord.Embed(colour=3447003)
        em.set_author(name = "Hal Has moved channels")
        await message.channel.send(embed=em)

    if str(message.content).upper().startswith("*VOLUME|"):
        Player.volume
        total= int(str(message.content).split('|')[1])
        Player.volume=total/100
        em = discord.Embed(colour=3447003)
        em.set_author(name="Music Volume has been changed to {0}".format(str(total))+"%." )
        Volume = total
        await message.channel.send(embed=em)

    if str(message.content).upper() == ("*STATUS"):
        em = discord.Embed(title="Status Update" , description=("Number of Fatal Errors: 0" + "\n" + "Last Restarted: " + str(Startup - datetime.datetime.now()) + " ago"), colour=3447003)
        em.set_author(name="Checked by " + str(message.author),icon_url=message.author.avatar_url)
        em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
        await message.channel.send( embed=em)

                                                                

    if str(message.content).upper()=='*MUSIC':
        misc=[]
        musc=[]
        OO=[]
        musicinfo=[]
        em = discord.Embed(title='Help',description="** *HelpCommands for command-specific information**",colour=DARK_NAVY)
        em.add_field(name="Miscellaneous", value="```"+ "*Test" + "\n" + "*Help" + "\n".join(misc) + "```")
        #em.add_field(name ="Music Info", value = "``" + "Name of Song/Video, Youtube Links, Soundcloud links, Spotify Links." + "``" +"\n".join(musicinfo))
        em.add_field(name="Music", value ="```"+"*Play|" + "\n" + "*Volume" + "\n"+ "*Resume" + "\n" + "*Pause" + "\n" + "*Move" + "\n" + "*Skip" + "\n" .join(musc) + "```")
        em.add_field(name="Owner Only", value="```"+ "*Restart" +"\n"+ "*Leave"  + "\n" .join(OO)+"```")
        em.set_footer(text="Hal | {:%b,%d %Y}".format(today))
        await message.channel.send(embed=em)
    
    if str(message.content).upper().startswith("*PLAY|"):
        
        if Player!=None:
            if message.guild.voice_client.is_playing():
                em = discord.Embed(colour = 3447033)
                em.set_author(name="Song In Progress! Once the song is done you can play your song. ")
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await message.channel.send(embed = em)
                #message.guild.voice_client.stop()
        try:
            query_string = urllib.parse.urlencode({"search_query" : str(message.content).split('|')[1]})
            req = urllib.request.Request("http://www.youtube.com/results?" + query_string)
            with urllib.request.urlopen(req) as html:
                searchresults = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
                link = ("http://www.youtube.com/watch?v=" + searchresults[0])        
            if message.guild.voice_client == None:
                Player = await YTDLSource.from_url(link,loop = client.loop)
                channel=message.author.voice.channel
                await channel.connect()
                MusicAuthorID = message.author.id
                while message.guild.voice_client == None:
                    await message.guild.voice_client.play(Player)
                Player = await YTDLSource.from_url(link,loop = client.loop)
                em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  + str(round(Player.duration/60)) +  ' Minutes' + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(Volume) +"%." + "``" + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                
                await message.channel.send( embed=em)
                message.guild.voice_client.play(Player)
            else:
                channel=message.author.voice.channel
                try:
                    Player = await YTDLSource.from_url(link,loop = client.loop)
                except exception as e:
                    channel=message.author.voice.channel
                    await channel.connect()
                    Player = await YTDLSource.from_url(link,loop = client.loop)
                message.guild.voice_client.play(Player)
                em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`' + str(round(Player.duration/60)) + ' Minutes' + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(Volume) + "%." + "``"  + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await message.channel.send(embed=em)                
        except IndexError:
            await message.channel.send ("Could not find this video on YouTube.")
            if(Player.is_playing == False):
                em= discord.Embed(description = Player.title +link+ "\n" + "**Song Has Ended**", colour = 3447003)
                em.set_author(name = "Music", icon_url=message.author.avatar_url)
                await message.channel.send(embed=em)

    if str(message.content).upper().upper() == ("*SKIP"):
        if message.author.id == MusicAuthorID:
            if Player!=None:
                if message.guild.voice_client.is_playing():
                    message.guild.voice_client.stop()
            em = discord.Embed(colour=3447003)
            em = discord.Embed(title="Skipped By " + str(message.author), icon_url=message.author.avatar_url , description=("Skipped Song: " + Player.title), colour=3447003)
            em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
            await message.channel.send(embed=em)
        if message.author.id!= MusicAuthorID:
            em = discord.Embed(colour = 3447033)
            em.set_author(name="You Can't Skip Other Peoples Songs")
            em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
            await message.channel.send(embed = em)
        
     
client.loop.run_until_complete(client.start(TokenDoc.token))
