import discord
import TokenDoc
import youtube_dl
import os
import re
import urllib
import datetime
import pafy


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
EMBEDCOLOR = 3447033
DARK_NAVY = 2899536
MusicAuthorID = ""
skip = False
pause = False
resume = False



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
            print ("Stream = " + stream)
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
async def background_loop():
    while True:
        
        import datetime
        global c_time

        c = datetime.datetime.now() - starttime

        print ("XD" + c) 
    
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
            print ("volume" + str(Vol))
            print ("total" + str(total))
            if (total < 200 and total > 0):
                em = discord.Embed(colour=3447003)
                em.set_author(name="Music Volume has been changed to {0}".format(str(total))+"%." )
                await message.channel.send(embed=em)
            if (total > 201 or total < 0):
                em = discord.Embed(colour=3447003)
                em.set_author(name="Volume Number Invalid")
                await message.channel.send(embed=em)

    
    if str(message.content).upper().startswith("*PLAY|"):
        skip = False
        pause = False
        resume = False
        MusicAuthorID == message.author.id
        currentlyplaying = False
        paused = False
        starttime = datetime.datetime.now()
        #inside the Queue add-
            #Clear
            #shuffle
            #remove
            #loop
            #skip
        if channel == None:
            em = discord.Embed(colour = 3447033)
            em.set_author(name="Please join a voice channel to start a song")
            em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
            await message.channel.send(embed = em)
            return
        if Player!=None:
            if message.guild.voice_client.is_playing():
                em = discord.Embed(title = "", descrption = ("Song In Progress! " + "**" + Player.title + "**" + " Has been added to the Queue"),colour = 3447033)
                em.set_author(name="Song Added To The Queue")
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await message.channel.send(embed = em)
                #message.guild.voice_client.stop()
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
            if message.guild.voice_client == None:
                Player = await YTDLSource.from_url(link,loop = client.loop)
                channel=message.author.voice.channel
                await channel.connect()
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
                em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`' + "0:00"  + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
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
                
                while second < sec or background == sec or skip:
                    background +=1
                    time.sleep(1)
                    second +=1
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
                            
                    em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  str(AIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
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
                        
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  "Paused" + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
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
                    if resume == True:
                        em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  +  str(AIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
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
                        break
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
                    print (e)
                    channel=message.author.voice.channel
                    await channel.connect()
                    Player = await YTDLSource.from_url(link,loop = client.loop)
                message.guild.voice_client.play(Player)
                em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`' + str(AIC) + "/" + str(BIC) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``"  + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
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
            if(Player.is_playing == False):
                em= discord.Embed(description = Player.title +link+ "\n" + "**Song Has Ended**", colour = 3447003)
                em.set_author(name = "Music", icon_url=message.author.avatar_url)
                await message.channel.send(embed=em)


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
