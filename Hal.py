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

Latest = requests.get("https://api.spacexdata.com/v3/launches/latest").text
json_Latest=json.loads(Latest)

Upcoming = requests.get("https://api.spacexdata.com/v3/launches/upcoming").text
json_Upcoming=json.loads(Upcoming)


today = datetime.date.today()
now = datetime.datetime.now()

print("Hal is Booting up...")

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
volume = "100%"

EMBEDCOLOR = 3447033
DARK_NAVY = 2899536
MusicAuthorID = ""
skip = False
pause = False
resume = False
loop = False
currentlyplaying = False
Queuetitle = None
Music_SOS = None
Live = False
songended = False

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
    #client.loop.add_task(background_loop())

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
        OO=[]
        em = discord.Embed(title='Help',description="** *HelpCommands for command-specific information**",colour=DARK_NAVY)
        em.add_field(name="Music", value ="```"+"*PLAY" + "\n" + "*VOLUME" + "\n"+ "*RESUME" + "\n" + "*PAUSE" + "\n" + "*SKIP" + "\n"  + "*LOOP"  + "\n".join(musc) + "```")
        em.add_field(name="Miscellaneous", value="```"+ "*TEST" + "\n" + "*STATUS" + "\n" + "*UPCOMING" + "\n" + "*COUNTDOWN" + "\n" + "*LAUNCHMODE" + "\n".join(misc) + "```")
        em.add_field(name="Owner Only", value="```"+ "*Restart" +"\n"+ "*Leave"  + "\n" .join(OO)+"```")
        em.set_footer(text=str(Footer))
        await message.channel.send(embed=em)
    if str(message.content).upper().startswith("*PLAY|"):
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
            em = discord.Embed(colour=3447003)
            em.set_author(name="Song Added To Queue")
            await message.channel.send(embed = em)
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
            print ("0")
            minute = 0
            second = 0 
            hourbruh = 0
            background = 0
            if channel == None:
                em = discord.Embed(colour = 3447033)
                em.set_author(name="Please join a voice channel to start a song")
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await message.channel.send(embed = em)
                return
            query_string = urllib.parse.urlencode({"search_query" : str(message.content).split('|')[1]})
            req = "http://www.youtube.com/results?"+query_string
            with urllib.request.urlopen(req) as html:
                searchresults=re.findall("watch\?v=(.{11})", requests.get(req).text)
                #searchresults = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
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
            sec = video.length
            currentlyplaying == True
            title = Player.title
            em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`' + "0:00"  + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(volume) + "``" + "\n" + "**" +  "Queue:" + "**" +  "\nNo Songs In Queue" ), colour=3447003)
            em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
            em.set_footer(text=str(Footer))
            Music_SOS = await message.channel.send(embed=em)
            starttime = datetime.datetime.now()
            secondoffset = 0
            message.guild.voice_client.play(Player)
            currentlyplaying = True
            while background > sec or second < video.length or skip or Live == False or background == sec:
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
                    em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  str(AIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(volume) + "``" + "\n"  + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                    em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                    em.set_footer(text=str(Footer))
                    await Music_SOS.edit(embed=em)
                    if pause == True:
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  "Paused" + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + str(volume) + "``" + "\n" + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                        em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                        em.set_footer(text=str(Footer))
                        await Music_SOS.edit(embed=em)
                    if loop == True:
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + "``" + '**' + "Song Looped" + "**" +  '``'), colour=3447003)
                        em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                        em.set_footer(text=str(Footer))
                        await Music_SOS.edit(embed=em)
                    if background == sec or skip == True:
                        background = 0
                        timenow = datetime.datetime.now()
                        second = 0
                        print ("Song is done")
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + "``" + '**' + "Song Has Ended" + "**" +  '``'), colour=3447003)
                        em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                        em.set_footer(text=str(Footer))
                        await Music_SOS.edit(embed=em)
                        currentlyplaying = False
                        if songended == True:
                            break
                        if len(Queue) < 0:
                            break 
                        if len(Queue) > 0:
                            print("Queue Start")
                            print (sec)
                            print (second)
                            print (background)
                            background = 0
                            second = 0
                            secondoffset = 0
                            starttime = datetime.datetime.now()
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
                                    BIC= str(hours)+":"+"0"+str(seconds)
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
                            print (second)
                            em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  str(AIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n"  + "**" + "Queue:" + "**" + str(QueueList)), colour=3447003)
                            em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                            em.set_footer(text=str(Footer))
                            await Music_SOS.edit(embed=em)          
                if second >= 59:
                    minute = int(minute)
                    secondoffset -= 60
                    minute += 1
                    await Music_SOS.delete()
                    Music_SOS = await message.channel.send(embed = em)
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

    if str(message.content).upper() == ("*QUEUE"):
        em = discord.Embed(colour = 3447033)
        em = discord.Embed(title= "Queue", description=(QueueList), colour=3447003)
        em.set_footer(text=str(Footer))
        await message.channel.send(embed = em)

          
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
                volume = "{0}".format(str(total))+"%"
                print (volume)
            if (total > 201 or total < 0):
                em = discord.Embed(colour=3447003)
                em.set_author(name="Volume Number Invalid")
                await message.channel.send(embed=em)

    if str(message.content).upper().upper() == ("*LOOP"):
        loop = True 
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
                    second = 0
                    background = 0
                    starttime = datetime.datetime.now()
                    secondoffset = 0      
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
