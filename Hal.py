import discord
import TokenDoc
import youtube_dl
import os
import re
import urllib
import copy
import datetime
import pafy
import logging
from typing import Dict
import aiohttp
from xml import etree
import requests
import json

Latest = requests.get("https://api.spacexdata.com/v3/launches/latest").text
json_Latest=json.loads(Latest)

Upcoming = requests.get("https://api.spacexdata.com/v3/launches/upcoming").text
json_Upcoming=json.loads(Upcoming)



print("Hal is Booting up...")
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
Queue = []

EMBEDCOLOR = 3447033
DARK_NAVY = 2899536
MusicAuthorID = ""
skip = False
pause = False
resume = False
currentlyplaying = False
Queuetitle = None
Music_SOS = None
Live = False




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
        if MS.duration == 0:
            MS.is_live = True
    @classmethod
    async def from_url(cls,url,*,loop=None,stream=False):
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download = False))
        if data.get('duration')==0 or data.get('duration')>3600:
            stream=True
            print ("Stream = " + str(stream))
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download = not stream))
        print ("Stream = False")
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
    global time_message
    global time_s
    global Blocked
    global MusicAuthorID
    global start
    global skip
    global pause
    global resume
    global loading
    global currentlyplaying
    global Queuetitle
    global Queue
    global QueueList
   
    global Live

    user = message.guild.get_member(HAL_ID)
    channel = None
    try:
        channel = message.author.voice.channel
    except Exception as e:
        print (e)
        print("Author not in voice channel")
        
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
            await message.channel.send(embed=em)

        if message.author.id==CREATOR_ID:
            em = discord.Embed(colour=3447003)
            em.set_author(name="Hal is restarting...")
            await message.channel.send(embed=em)
            client.loop.run_until_complete(client.logout())
            os.system("python3 /usr/bin/python3.6 /home/pi/Hal.py")
            raise SystemExit
        
    if str(message.content).upper().upper()==("*MOVE"):
        await user.edit(voice_channel = channel)
        em = discord.Embed(colour=3447003)
        em.set_author(name = "Hal Has moved channels")
        await message.channel.send(embed=em)

    if str(message.content).upper() == ("*STATUS"):
        em = discord.Embed(title="Status Update" , description=("Number of Fatal Errors: 0" + "\n" + "Last Restarted: " + str(datetime.datetime.now() - Startup) + " ago"), colour=3447003)
        em.set_author(name="Checked by " + str(message.author),icon_url=message.author.avatar_url)
        em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
        await message.channel.send( embed=em)
     
    if str(message.content).upper().startswith("*VOLUME|"):
        if Player == None:
            em = discord.Embed(colour=3447003)
            em.set_author(name = "Hal Is Not In A Voice Channel")
            await message.channel.send(embed=em)
        if Player != None:
            Vol = Player.volume
            total= int(str(message.content).split('|')[1])
            Vol=total/100
            if (total < 200 and total > 0):
                em = discord.Embed(colour=3447003)
                em.set_author(name="Music Volume has been changed to {0}".format(str(total))+"%." )
                await message.channel.send(embed=em)
            if (total > 201 or total < 0):
                em = discord.Embed(colour=3447003)
                em.set_author(name="Volume Number Invalid")
                await message.channel.send(embed=em)

    if str(message.content).upper() == ("*LAUNCHES"):
        em = discord.Embed(title=  "Latest Launch", description=("**" + "Misson Name:\n" + "**" + "``" + str(json_Latest["mission_name"]) + "``\n" + "**" "Rocket Model:\n" + "**" + "``"+ str(json_Latest["rocket"]["rocket_name"] + "``\n" + "**" + "Launch Time:\n" + "**" + "``" + str(json_Latest["launch_date_local"] + "``"))), colour=3447003)
        em.set_author(name="Checked by " + str(message.author),icon_url=message.author.avatar_url)
        em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
        await message.channel.send( embed=em)
    if str(message.content).upper() == ("*UPCOMING"):
        em = discord.Embed(title=  "Upcoming Launch", description=("**" + "Mission Name:\n" + "**" + "``" + str(json_Upcoming[0]["mission_name"]) + "``\n" + "**" + "Rocket Model:\n" + "**" + "``" + str(json_Upcoming[0]["rocket"]["rocket_name"] + "``\n" + "**" + "Launches Time:\n" + "**" + "``" + str(json_Upcoming[0]["launch_date_local"] + "``"))) , colour=3447003)
        em.set_author(name="Checked by " + str(message.author),icon_url=message.author.avatar_url)
        em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
        await message.channel.send( embed=em)
    
    if str(message.content).upper().startswith("*PLAY|"):
        skip = False
        pause = False
        resume = False
        MusicAuthorID == message.author.id
        paused = False
        starttime = datetime.datetime.now()
        if message.guild.voice_client == None:
            channel=message.author.voice.channel
            await channel.connect()
        else:
             await user.edit(voice_channel = channel)
        if len(Queue)<1:
            QueueList="\nNo Songs In Queue"
        if currentlyplaying == True:
            em = discord.Embed(colour=3447003)
            em.set_author(name="Song Added To Queue")
            await message.channel.send(embed = em)
            query_string = urllib.parse.urlencode({"search_query" : str(message.content).split('|')[1]})
            req = urllib.request.Request("http://www.youtube.com/results?" + query_string)
            with urllib.request.urlopen(req) as html:
                searchresults = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
                link = ("http://www.youtube.com/watch?v=" + searchresults[0])
                QueueInfo = await YTDLSource.from_url(link,loop = client.loop)
                print (QueueInfo.title)
                url = (link)
            if "youtube.com" in url:
                youtube = etree.HTML(urllib.request.urlopen(url).read())
                name=youtube.xpath("//span[@id='eow-title']/@title")
                Queue.append([name,url])
                QueueList = ""
                for x in Queue:
                    QueueList += "\n" + "["+ x[0][0] + "]" "("+x[1]+")"    
        if currentlyplaying == False:
            currentlyplaying == True
            if channel == None:
                em = discord.Embed(colour = 3447033)
                em.set_author(name="Please join a voice channel to start a song")
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await message.channel.send(embed = em)
                return
            try:
                query_string = urllib.parse.urlencode({"search_query" : str(message.content).split('|')[1]})
                req = urllib.request.Request("http://www.youtube.com/results?" + query_string)
                with urllib.request.urlopen(req) as html:
                    searchresults = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
                    link = ("http://www.youtube.com/watch?v=" + searchresults[0])
                    url = (link)
                    video = pafy.new(url)
                    minutes = int(video.length/60)
                    seconds = int(video.length-(minutes*60))
                    hours = int(minutes/60)
                    if hours > 0:
                        minutes = minutes-(hours*60)
                        if len(str(minutes))==1:
                            minutes="0"+str(minutes)
                        if len(str(seconds)) == 1:
                            BIC= str(hours)+":"+"0"+str(seconds)
                        else:
                            BIC = str(hours)+":"+str(minutes)+":"+str(seconds)
                    else:
                        if len(str(seconds)) ==1:
                            BIC = str(minutes)+":"+"0"+str(seconds)
                        else:
                            BIC = str(minutes)+":"+str(seconds)
                
                if video.length < 1:
                    Live = True     
                Player = await YTDLSource.from_url(link,loop = client.loop)
                MusicAuthorID = message.author.id
                while message.guild.voice_client == None:
                    await message.guild.voice_client.play(Player)
                Player = await YTDLSource.from_url(link,loop = client.loop)
                import time
                minute = 0
                second = 0 
                hourbruh = 0
                background = 0
                sec = video.length
                currentlyplaying == True
                title = Player.title
                em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`' + "0:00"  + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n" + "**" +  "Queue:" + "**" +  "\nNo Songs In Queue" ), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                now = datetime.datetime.now()
                AMPM = ""
                hour = now.hour
                if now.hour < 13:
                    AMPM = "AM"
                else:
                    AMPM = "PM"
                    hour = hour -12
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today) + " at " + str(hour) + ":" +  str(now.minute) + AMPM)
                Music_SOS = await message.channel.send(embed=em)
                message.guild.voice_client.play(Player)
                currentlyplaying = True
               
                while second < sec or background == sec or skip or Live == False:
                    background +=1
                    time.sleep(1)
                    second +=1
                    if Live == True:
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  "Now Streaming" + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n" + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                        em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                        now = datetime.datetime.now()
                        AMPM = ""
                        hour = now.hour
                        if now.hour < 13:
                            AMPM = "AM"
                        else:
                            AMPM = "PM"
                            hour = hour -12
                        em.set_footer(text="Hal | {:%b, %d %Y}".format(today) + " at " + str(hour) + ":" +  str(now.minute) + AMPM)
                        await Music_SOS.edit(embed=em)
                     
                    if Live == False:
                        if hour > 0:
                            minute = int(minute)-(hourbruh*60)
                            if len(str(minute))== 1:
                                minute= "0" + str(minute)
                            if len(str(second)) == 1:
                                AIC= str(minute)+":"+"0"+str(second)
                            else:
                                AIC = str(minute)+":"+str(second)
                        else:
                            if len(str(second)) ==1:
                                AIC = str(minute)+":"+"0"+str(second)
                            else:
                                AIC = str(minute)+":"+str(second)
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  str(AIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n"  + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                        em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                        now = datetime.datetime.now()
                        AMPM = ""
                        hour = now.hour
                        if now.hour < 13:
                            AMPM = "AM"
                        else:
                            AMPM = "PM"
                            hour = hour -12
                        em.set_footer(text="Hal | {:%b, %d %Y}".format(today) + " at " + str(hour) + ":" +  str(now.minute) + AMPM)
                        await Music_SOS.edit(embed=em)
                        if pause == True:
                            em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  "Paused" + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n" + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                            em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                            now = datetime.datetime.now()
                            AMPM = ""
                            hour = now.hour
                            if now.hour < 13:
                                AMPM = "AM"
                            else:
                                AMPM = "PM"
                                hour = hour -12
                            em.set_footer(text="Hal | {:%b, %d %Y}".format(today) + " at " + str(hour) + ":" +  str(now.minute) + AMPM)
                            await Music_SOS.edit(embed=em)
                        if background == sec:
                            em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + "``" + '**' + "Song Has Ended" + "**" +  '``'), colour=3447003)
                            em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                            now = datetime.datetime.now()
                            AMPM = ""
                            hour = now.hour
                            if now.hour < 13:
                                AMPM = "AM"
                            else:
                                AMPM = "PM"
                                hour = hour -12
                            em.set_footer(text="Hal | {:%b, %d %Y}".format(today) + " at " + str(hour) + ":" +  str(now.minute) + AMPM)
                            await Music_SOS.edit(embed=em)
                            currentlyplaying = False
                            if len(Queue) >0:
                                background = 0
                                second = 0
                                print ("Second" + str(second))
                                print ("Background" + str(background))
                                print ("AIC" + str(AIC))
                                print ("BIC" + str(BIC))
                                currentlyplaying = True
                                Player = await YTDLSource.from_url(Queue[0][1],loop = client.loop)
                                sec = Player.data["duration"]
                                minutes = int(sec/60)
                                seconds = int(sec-(minutes*60))
                                hours = int(sec/60)
                                if hours > 0:
                                    minutes = minutes-(hours*60)
                                    if len(str(minutes))==1:
                                        minutes="0"+str(minutes)
                                    if len(str(seconds)) == 1:
                                        CIC= str(hours)+":"+"0"+str(seconds)
                                    else:
                                        CIC = str(hours)+":"+str(minutes)+":"+str(seconds)
                                else:
                                    if len(str(seconds)) ==1:
                                        CIC = str(minutes)+":"+"0"+str(seconds)
                                    else:
                                        CIC = str(minutes)+":"+str(seconds)
                                Queue.remove(Queue[0])
        
                                QueueList = ""
                                for x in Queue:
                                    QueueList += "\n" + "["+ x[0][0] + "]" "("+x[1]+")"
                                message.guild.voice_client.play(Player)
                                em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  str(AIC) + "/" + str(CIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n"  + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                                now = datetime.datetime.now()
                                AMPM = ""
                                hour = now.hour
                                if now.hour < 13:
                                    AMPM = "AM"
                                else:
                                    AMPM = "PM"
                                    hour = hour -12
                                em.set_footer(text="Hal | {:%b, %d %Y}".format(today) + " at " + str(hour) + ":" +  str(now.minute) + AMPM)
                                await Music_SOS.edit(embed=em)
                        if second == 59:
                            minute = int(minute)
                            second = 0
                            minute += 1
                        if minute == 60:
                            minute = int(minute)
                            second = 0
                            minute = 0
                            hourbruh += 1    
                else:
                    channel=message.author.voice.channel
                    try:
                        Player = await YTDLSource.from_url(link,loop = client.loop)
                    except Exception as e:
                        channel=message.author.voice.channel
                        await channel.connect()
                        Player = await YTDLSource.from_url(link,loop = client.loop)
                    message.guild.voice_client.play(Player)
                
                    em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`' + str(AIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``"  + "\n" +  "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                    em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                    now = datetime.datetime.now()
                    AMPM = ""
                    hour = now.hour
                    if now.hour < 13:
                        AMPM = "am"
                    else:
                        AMPM = "pm"
                        hour = hour -12
                    em.set_footer(text="Hal | {:%b, %d %Y}".format(today) + " at " + str(hour) + ":" +str(now.minute) + AMPM)
                    await message.channel.send(embed=em)
            except IndexError:
                await message.channel.send ("Could not find this video on YouTube.")
               


    if str(message.content).upper().upper() == ("*PAUSE"):
        pause = True
        resume = False
        message.guild.voice_client.pause()
        
    if str(message.content).upper().upper() == ("*RESUME"):
        resume = True
        pause= False
        message.guild.voice_client.resume()
        
    if str(message.content).upper().upper() == ("*SKIP"):
        
        skip = True 
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
