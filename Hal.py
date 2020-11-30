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
from lxml import etree
import requests
import json
import ffmpeg
import asyncio


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
Users = []
Queue = []
Leaderboard = []
volume = "100%"

EMBEDCOLOR = 3447033
DARK_NAVY = 2899536
MusicAuthorID = ""
skip = False
pause = False
resume = False
loop = False
Leave = False
currentlyplaying = False
Queuetitle = None
Music_SOS = None
Live = False
songended = False
ResumeMSG = False
PauseMSG = False


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

@client.event
async def on_ready():
    import time
    await client.change_presence(activity=discord.Game(name= "*Countdown", type = 1, url="https://www.youtube.com/watch?v=NiUmFQY3LNA"))

@client.event
async def on_voice_state_update(member, before, after):
    try:
        server = after.channel.guild
    except AttributeError:
        server = before.channel.guild
    user = server.get_member(HAL_ID)
    users = []
    if before !=None and server.get_member(HAL_ID).voice !=None:
        if before.channel != server.get_member(HAL_ID).voice.channel:
            return
    try:
        for user in server.get_member(HAL_ID).voice.channel.members:
            if user.bot == False:
                users.append(user)
        if len(users)==0:
            server.voice_client.pause()
            print("paused")     
    except AttributeError:
        print("Error")            
            
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
    global Leave
    global pause
    global loop
    global resume
    global loading
    global currentlyplaying
    global Queuetitle
    global Queue
    global QueueList
    global volume
    global Live
    global AIC
    global ResumeMSG
    global PauseMSG


    today = datetime.date.today()
    now = datetime.datetime.now()


    Latest = requests.get("https://api.spacexdata.com/v3/launches/latest").text
    json_Latest=json.loads(Latest)

    Upcoming = requests.get("https://api.spacexdata.com/v3/launches/upcoming").text
    json_Upcoming=json.loads(Upcoming)

    liftoff = str(now)
    countdowntimer = str(json_Upcoming[0]["launch_date_local"])
    s = countdowntimer.split('T')
    a = s[0].split('-')
    t = s[1].split('-')
    u = t[0].split(',')
    v = u[0].split(':')
    launch = a + v
    launchtime = []
    for e in launch:
        launchtime.append(int (e))
        
    launchtime[3]=launchtime[3]-4   
    launchdatetime = datetime.datetime(*launchtime)
    looplaunch = launchdatetime-now


    leaderboard_string = "```  # Username             # Of Gifs Sent\n -----------------------------------------```"

    if str(message.content).startswith("https://tenor.com"):
        print("gif added")
       
    AMPM = ""
    hour = now.hour
    if now.hour < 13:
        AMPM = "AM"
    else:
        AMPM = "PM"
        hour = hour -12
    Footer = "Hal | {:%b, %d %Y}".format(today) + " at " + str(hour) + ":" +  str(now.minute) + AMPM

    user = message.guild.get_member(HAL_ID)
    channel = None
    try:
        channel = message.author.voice.channel
    except Exception as e:
        print (e)
         
    if str(message.content).upper() == ("*TEST"):
        await message.channel.send("`Test Complete`")   
    if str(message.content).upper() == ("*RESTART"):
        if message.author.id!=CREATOR_ID:
            await message.channel.send("`This Command Is A Creator Only Command.`")
        if message.author.id==CREATOR_ID:
            await message.channel.send("`Hal Is Restarting...`")
            client.loop.run_until_complete(client.logout())
            os.system("python3 /usr/bin/python3.6 /home/pi/Hal.py")
            raise SystemExit
    if str(message.content).upper().upper()==("*MOVE"):
        await user.edit(voice_channel = channel)
        await message.channel.send("`Hal Has moved channels`")
    if str(message.content).upper() == ("*STATUS"):
        em = discord.Embed(title="Status Update" , description=("Number of Fatal Errors: 0" + "\n" + "Last Restarted: " + str(datetime.datetime.now() - Startup) + " ago"), colour=3447003)
        em.set_author(name="Checked by " + str(message.author),icon_url=message.author.avatar_url)
        em.set_footer(text=str(Footer))
        await message.channel.send(embed=em)
    if str(message.content).upper() == ("*LAUNCHES"):
        em = discord.Embed(title=  "Latest Launch", description=("**" + "Misson Name:\n" + "**" + "``" + str(json_Latest["mission_name"]) + "``\n" + "**" "Rocket Model:\n" + "**" + "``"+ str(json_Latest["rocket"]["rocket_name"] + "``\n" + "**" + "Launch Time:\n" + "**" + "``" + str(json_Latest["launch_date_local"] + "``"))), colour=3447003)
        em.set_author(name="Checked by " + str(message.author),icon_url=message.author.avatar_url)
        em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
        await message.channel.send( embed=em)
    if str(message.content).upper() == ("*UPCOMING"):
        em = discord.Embed(title=  "Upcoming Launch", description=("**" + "Mission Name:\n" + "**" + "``" + str(json_Upcoming[0]["mission_name"]) + "``\n" + "**" + "Rocket Model:\n" + "**" + "``" + str(json_Upcoming[0]["rocket"]["rocket_name"] + "``\n" + "**" + "Launches Time:\n" + "**" + "``" + str(json_Upcoming[0]["launch_date_local"] + "``"))) , colour=3447003)
        em.set_author(name="Checked by " + str(message.author),icon_url=message.author.avatar_url)
        em.set_footer(text=str(Footer))
        await message.channel.send( embed=em)
    if str(message.content).upper() == ("*COUNTDOWN"):
        em = discord.Embed(colour=3447003)
        em.set_author(name =  str(looplaunch).split('.')[0] +  " Until Next SpaceX Launch!")
        await message.channel.send(embed=em)
    if str(message.content).upper() == ("*LAUNCHMODE"):
        em = discord.Embed(colour=15158332)
        em.set_author(name = "Launch Mode Activated... \nSending Info about todays launch")
        await message.channel.send(embed=em)
        em = discord.Embed(title="Upcoming Launch", description=("**" + "Mission Name:\n" + "**" + "``" + str(json_Upcoming[0]["mission_name"]) + "``\n" + "**" + "Rocket Model:\n" + "**" + "``" + str(json_Upcoming[0]["rocket"]["rocket_name"] + "``\n" + "**" + "Countdown:\n" + "**" + "``" + str(looplaunch)+ "``")) , colour=15158332)
        em.set_author(name="")
        em.set_footer(text=str(Footer))
        await message.channel.send(embed=em)
    if str(message.content).upper()==('*HELP'):
        misc=[]
        musc=[]
        em = discord.Embed(title='Help',description="Command List",colour=DARK_NAVY)
        em.add_field(name="Music", value ="```"+"*PLAY|" + "\n" + "*QUEUE" + "\n" + "*VOLUME" + "\n"+ "*RESUME" + "\n" + "*PAUSE" + "\n" + "*SKIP" + "\n".join(musc) + "```")
        em.add_field(name="Miscellaneous", value="```"+ "*TEST" + "\n" + "*STATUS" + "\n" + "*UPCOMING" + "\n" + "*COUNTDOWN" + "\n" + "*LAUNCHMODE" + "\n" + "*LEAVE" + "\n".join(misc) + "```")
        em.set_footer(text=str(Footer))
        await message.channel.send(embed=em)
        
    if str(message.content).upper().startswith("*PLAY|"):
        Leave = False
        skip = False
        pause = False
        resume = False
        songended = False 
        MusicAuthorID == message.author.id
        paused = False 
        if message.guild.voice_client == None:
            channel=message.author.voice.channel
            await channel.connect()
        else:
             await user.edit(voice_channel = channel)
        if len(Queue)<1:
            QueueList="\nNo Songs In Queue"
        if currentlyplaying == True:
            if channel == None:
                await message.channel.send("`Please join a voice channel to start a song`")
                return
            await message.channel.send("`Song Added To Queue`")
            query_string = urllib.parse.urlencode({"search_query" : str(message.content).split('|')[1]})
            req = "http://www.youtube.com/results?"+query_string
            with urllib.request.urlopen(req) as html:
                searchresults=re.findall("watch\?v=(.{11})", requests.get(req).text)
                #searchresults = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
                link = ("http://www.youtube.com/watch?v=" + searchresults[0])
                QueueInfo = await YTDLSource.from_url(link,loop = client.loop)
                print (QueueInfo.title)
                url = (link)
            if "youtube.com" in url:
                #youtube = etree.HTML(urllib.request.urlopen(url).read())
                #name=youtube.xpath("//span[@id='eow-title']/@title")
                from bs4 import BeautifulSoup
                page=requests.get(url).text
                soup=BeautifulSoup(page,features='html.parser')
                name=soup.find('meta',{'property':'og:title'})['content']
                Queue.append([name,url])
                
                QueueList = ""
                for x in Queue:
                    print ("que") 
                    print (str (x[0]))
                    QueueList += "\n" + "["+ str(x[0])+ "]" + "("+str(x[1])+")"
                    
        if currentlyplaying == False:
            currentlyplaying == True
            if channel == None:
                await message.channel.send("`Please join a voice channel to start a song`")
                return
            query_string = urllib.parse.urlencode({"search_query" : str(message.content).split('|')[1]})
            req = "http://www.youtube.com/results?"+query_string
            with urllib.request.urlopen(req) as html:
                searchresults=re.findall("watch\?v=(.{11})", requests.get(req).text)
                #searchresults = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
                link = ("http://www.youtube.com/watch?v=" + searchresults[0])
                url = (link)
                Player = await YTDLSource.from_url(link,loop = client.loop)
                MusicAuthorID = message.author.id
                while message.guild.voice_client == None:
                    await message.guild.voice_client.play(Player)
                Player = await YTDLSource.from_url(link,loop = client.loop)
                minutes = int(Player.duration/60)
                seconds = int(Player.duration-(minutes*60))
                hours = int(minutes/60)
                #minutes-=hours*60
                if hours > 0:
                    minutes = minutes-(hours*60)
                    if len(str(minutes))==1:
                        minutes="0"+str(minutes)
                    if len(str(seconds)) == 1:
                        BIC= str(hours)+":"+str(minutes)+":"+"0"+str(seconds)
                    else:
                        BIC = str(hours)+":"+str(minutes)+":"+str(seconds)
                else:
                    if len(str(seconds)) ==1:
                        BIC = str(minutes)+":"+"0"+str(seconds)
                    else:
                        BIC = str(minutes)+":"+str(seconds)
            if Player.duration < 1:
                Live = True    
            import time
            sec = Player.duration
            currentlyplaying == True
            title = Player.title
            em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`' + "0:00"  + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(volume) + "``" + "\n" + "**" +  "Queue:" + "**" +  "\nNo Songs In Queue" ), colour=3447003)
            em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
            em.set_footer(text=str(Footer))
            Music_SOS = await message.channel.send(embed=em)
            minute = 0
            second = 0 
            hourbruh = 0
            background = 0
            starttime = datetime.datetime.now()
            secondoffset = 0
            message.guild.voice_client.play(Player)
            currentlyplaying = True
            while background > sec or skip or Leave or Live == False or background == sec:
                if Leave == True:
                    break
                if skip == True:
                    break
                import time
                timenow = datetime.datetime.now()
                skip = False
                background +=1
                time.sleep(1)
                second = (timenow - starttime).seconds + secondoffset
                if Live == True:
                    em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  "Now Streaming" + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(volume) + "``" + "\n" + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                    em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                    em.set_footer(text=str(Footer))
                    await Music_SOS.edit(embed=em)
                if Live == False:
                    if hourbruh > 0:
                        minute = int(minute)-(hourbruh*60)
                        if len(str(minute))== 1:
                            minute= "0" + str(minute)
                        if len(str(second)) == 1:
                            AIC= str(hourbruh)+":"+str(minutes)+":"+"0"+str(seconds)
                        else:
                            AIC = str(hoursbruh)+":"+str(minutes)+":"+str(seconds)
                    else:
                        if len(str(second)) ==1:
                            AIC = str(minute)+":"+"0"+str(second)
                        else:
                            AIC = str(minute)+":"+str(second)
                    em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  str(AIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(volume) + "``" + "\n"  + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                    em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                    em.set_footer(text=str(Footer))
                    try:
                        await Music_SOS.edit(embed=em)
                        
                    except discord.errors.NotFound:
                         Music_SOS = await message.channel.send(embed = em)
                    if pause == True:
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  "Paused" + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(volume) + "``" + "\n" + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                        em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                        em.set_footer(text=str(Footer))
                        await Music_SOS.edit(embed=em)
                    if loop == True:
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + "``" + str(AIC) + "/" + str(BIC) + "`" + '**' + "Song Looped" + "**" +  '``'), colour=3447003)
                        em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                        em.set_footer(text=str(Footer))
                        await Music_SOS.edit(embed=em)
                    if background == sec or Leave or skip == True:
                        background = 0
                        timenow = datetime.datetime.now()
                        second = 0
                        print ("Song is done")
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + "``" + '**' + "Song Has Ended" + "**" +  '``'), colour=3447003)
                        em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                        em.set_footer(text=str(Footer))
                        await Music_SOS.edit(embed=em)
                        await Music_SOS.delete()
                        currentlyplaying = False
                        if songended == True:
                            break
                        if len(Queue) == 0:
                            break 
                        if len(Queue) > 0:
                            background = 0
                            second = 0
                            secondoffset = 0
                            starttime = datetime.datetime.now()
                            timenow = datetime.datetime.now()
                            second = (timenow - starttime).seconds + secondoffset
                            currentlyplaying = True
                            Player = await YTDLSource.from_url(Queue[0][1],loop = client.loop)
                            sec = Player.data["duration"]
                            minutes = int(sec/60)
                            seconds = int(sec-(minutes*60))
                            hours = int(minutes/60)
                            if hours > 0:
                                minutes = minutes-(hours*60)
                                if len(str(minutes))==1:
                                    minutes="0"+str(minutes)
                                if len(str(seconds)) == 1:
                                    BIC= str(hours)+":"+str(minutes)+":"+"0"+str(seconds)
                                else:
                                    BIC = str(hours)+":"+str(minutes)+":"+str(seconds)
                            else:
                                if len(str(seconds)) ==1:
                                    BIC = str(minutes)+":"+"0"+str(seconds)
                                else:
                                    BIC = str(minutes)+":"+str(seconds)
                            Queue.remove(Queue[0])
                            QueueList = ""
                            for x in Queue:
                                QueueList += "\n" + "["+ x[0][0] + "]" "("+x[1]+")"
                            if len(Queue)<1:
                                QueueList="\nNo Songs In Queue"
                            message.guild.voice_client.play(Player)
                            skip = False
                            if Live == False:
                                second = 0
                                minute = 0 
                                if hour > 0:
                                    minute = int(minute)-(hourbruh*60)
                                    if len(str(minute))== 1:
                                        minute= "0" + str(minute)
                                    if len(str(second)) == 1:
                                        CIC= str(minute)+":"+"0"+str(second)
                                    else:
                                        CIC = str(hours)+":"+str(minutes)+":"+str(seconds)
                                else:
                                    if len(str(second)) ==1:
                                        CIC = str(minute)+":"+"0"+str(second)
                                    else:
                                        CIC = str(minute)+":"+str(second)
                            em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  str(CIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n"  + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                            em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                            em.set_footer(text=str(Footer))
                            Music_SOS = await message.channel.send(embed = em)
                            #await Music_SOS.edit(embed=em)

                if second == 30:
                    await Music_SOS.delete()
                    Music_SOS = await message.channel.send(embed = em)
                if second >= 59:
                    minute = int(minute)
                    secondoffset -= 60
                    minute += 1
                if minute == 60:
                    minute = int(minute)
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
                em.set_footer(text=str(Footer))
                await message.channel.send(embed=em)

            secondoffset = 0
            second = 0 
            starttime = datetime.datetime.now()
                #except IndexError:
                #    await message.channel.send ("Could not find this video on YouTube.")
                

        if currentlyplaying == False and len(Queue) == 0:
            await asyncio.sleep(30)
            await message.guild.voice_client.disconnect()
            LeaveMSG = await message.channel.send("`Hal Has left the voice channel`")
            await asyncio.sleep(120)
            await LeaveMSG.delete()    
            
    if str(message.content).upper() == ("*QUEUE"):
        em = discord.Embed(colour = 3447033)
        em = discord.Embed(title= "Queue", description=(QueueList), colour=3447003)
        em.set_footer(text=str(Footer))
        await message.channel.send(embed = em)

    
    if str(message.content).upper() == ("*GIFLB"):
        em = discord.Embed(colour = 3447033)
        em = discord.Embed(title= "GIF Leaderboard", description=(leaderboard_string), colour=3447003)
        em.set_footer(text=str(Footer))
        await message.channel.send(embed = em)

    if str(message.content).upper() == ("*LEAVE"):
        if Player == None:
            await message.channel.send("`Hal Is Not In A Voice Channel`")
        if Player != None:
            Leave = True
            Queue = []
            await message.guild.voice_client.disconnect()
            #Player = None
            await message.channel.send("`Hal has been disconnected from the voice channel`")
        
    if str(message.content).upper().startswith("*VOLUME|"):
        if Player == None:
            await message.channel.send("`Hal Is Not In A Voice Channel`")
        if Player != None:
            Vol = Player.volume
            total= int(str(message.content).split('|')[1])
            Vol=total/100
            if (total < 200 and total > 0):
                em = discord.Embed(colour=3447003)
                volume = "{0}".format(str(total))+"%"
                print (volume)
            if (total > 201 or total < 0):
                await message.channel.send("`Volume Number Invalid`")

    if str(message.content).upper().upper() == ("*LOOP"):
        loop = True
        
    if str(message.content).upper().upper() == ("*PAUSE"):
        pause = True
        resume = False
        message.guild.voice_client.pause()
        
    if str(message.content).upper().upper() == ("*RESUME"):
        await message.channel.send("`Music Resumed.`")
        resume = True
        pause= False
        message.guild.voice_client.resume()
        
    if str(message.content).upper().upper() == ("*SKIP"):
        if Player == None:
            await message.channel.send("`Hal is not in a voice channel`")
            skip = True
            if Player!=None:
                if message.guild.voice_client.is_playing():
                    message.guild.voice_client.stop()
                    second = 0
                    background = 0
                    starttime = datetime.datetime.now()
                    secondoffset = 0      
                await message.channel.send("`Song Skipped`")
                
client.loop.run_until_complete(client.start(TokenDoc.token))
