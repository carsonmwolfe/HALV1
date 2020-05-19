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
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download = False))
        if data.get('duration')==0 or data.get('duration')>3600:
            stream=True
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
    Volume = 1.0
    import datetime
    global time_message
    global time_s
    global Blocked

    user = message.guild.get_member(HAL_ID)
    channel = None
    try:
        channel = message.author.voice.channel
    except:
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
            os.system("python3 /home/pi/Hal.py")
            raise SystemExit
        
    if str(message.content).upper().upper()==("*MOVE"):
        await user.edit(voice_channel = channel)
        em = discord.Embed(colour=3447003)
        em.set_author(name = "Hal Has moved channels")
        await message.channel.send(embed=em)

    if str(message.content).upper().startswith("*BLOCK|"):
        if message.author.id!=CREATOR_ID:
            em = discord.Embed(colour=3447003)
            em.set_author(name="This Command Is a Creator Only Command!")
            await message.channel.send(embed=em)
        if message.author.id==CREATOR_ID:
            Blocked.append(message.guild.get_member_named(str(message.content).split('|')[1]))
            em = discord.Embed(colour=3447003)
            em.set_author(name="{0} Has Been Blocked.".format(str(message.guild.get_member_named(str(message.content).split('|')[1]))))
            await message.channel.send(embed=em)
        else:
            em = discord.Embed(colour=3447003)
            em.set_author(name="This is a Admin Only command.")

    if str(message.content).upper().startswith("*UNBLOCK|"):
        if message.author.id!=CREATOR_ID:
            em = discord.Embed(colour=3447003)
            em.set_author(name="This Command Is A Creator Only Command.")
            await message.channel.send(embed=em)
        if message.author.id==CREATOR_ID:
            Blocked.remove(message.guild.get_member_named(str(message.content).split('|')[1]))
            em = discord.Embed(colour=3447003)
            em.set_author(name="{0} Has Been Unblocked.".format(str(message.guild.get_member_named(str(message.content).split('|')[1]))))
            await message.channel.send(embed=em)

    if str(message.content).upper() == ("*BLOCKLIST"):
        em = discord.Embed(colour = 3447033)
        em.set_author(name="BlockList: "  + str(Blocked))
        await message.channel.send(embed = em)
         
    if str(message.content).upper() == ("*STATUS"):
        em = discord.Embed(title="Status Update" , description=("Number of Fatal Errors: 0" + "\n" + "Last Restarted: " + str(datetime.datetime.now() - Startup) + " ago"), colour=3447003)
        em.set_author(name="Checked by " + str(message.author),icon_url=message.author.avatar_url)
        em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
        await message.channel.send( embed=em)

    saga = datetime.date(2020,10,20) - datetime.date.today()

    if str(message.content).upper() == ("*COUNTDOWN"):
        em = discord.Embed(colour = 3447033)
        em.set_author(name=saga)
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
            print ("volume" + str(Vol))
            print ("total" + str(total))
            if (total < 200 and total > 0):
                em = discord.Embed(colour=3447003)
                em.set_author(name="Music Volume has been changed to {0}".format(str(total))+"%." )
                Volume = total
                await message.channel.send(embed=em)
            if (total > 201 or total < 0):
                em = discord.Embed(colour=3447003)
                em.set_author(name="Volume Number Invalid")
                await message.channel.send(embed=em)
                                               
    if str(message.content).upper()=='*MUSIC':
        misc=[]
        musc=[]
        OO=[]
        em = discord.Embed(title='Help',description="** *HelpCommands for command-specific information**",colour=DARK_NAVY)
        em.add_field(name="Miscellaneous", value="```"+ "*Test" + "\n" + "*Help" + "\n".join(misc) + "```")
        #em.add_field(name ="Music Info", value = "``" + "Name of Song/Video, Youtube Links, Soundcloud links, Spotify Links." + "``" +"\n".join(musicinfo))
        em.add_field(name="Music", value ="```"+"*Play|" + "\n" + "*Volume" + "\n"+ "*Resume" + "\n" + "*Pause" + "\n" + "*Move" + "\n" + "*Skip" + "\n" .join(musc) + "```")
        em.add_field(name="Owner Only", value="```"+ "*Restart" +"\n"+ "*Leave"  + "\n" .join(OO)+"```")
        em.set_footer(text="Hal | {:%b,%d %Y}".format(today))
        await message.channel.send(embed=em)
        
    
    if str(message.content).upper().startswith("*PLAY|"):
        if channel == None:
            em = discord.Embed(colour = 3447033)
            em.set_author(name="Please join a voice channel to start a song")
            em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
            await message.channel.send(embed = em)
            return
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
                url = (link)
                video = pafy.new(url)
                v_min, v_sec = divmod(video.length,60)
                v_hours = int(v_min/60)
                v_min = v_min%60
                
            if message.guild.voice_client == None:
                Player = await YTDLSource.from_url(link,loop = client.loop)
                channel=message.author.voice.channel
                await channel.connect()
                MusicAuthorID = message.author.id
                while message.guild.voice_client == None:
                    await message.guild.voice_client.play(Player)
                Player = await YTDLSource.from_url(link,loop = client.loop)
                
                em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`'  + str(v_hours) + ":" +  str(v_min) + ":" + str(v_sec) + "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``" + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
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
                await message.channel.send(embed=em)
                message.guild.voice_client.play(Player)
            else:
                channel=message.author.voice.channel
                try:
                    Player = await YTDLSource.from_url(link,loop = client.loop)
                except exception as e:
                    print (e)
                    channel=message.author.voice.channel
                    await channel.connect()
                    Player = await YTDLSource.from_url(link,loop = client.loop)
                message.guild.voice_client.play(Player)
                em = discord.Embed(title="" , description=("["+ Player.title + "]" "("+link+")"+ "\n" + '**' + 'Duration: ' + '**' + '`' + str(v_hours) + ":" + str(v_min) + ":" + str(v_sec)+ "`" +   '\n' + '**' + 'Volume:  '+ '**' + "``" + "100%" + "``"  + "\n" + "``" + "*Music For Full List Of Commands " + '``'), colour=3447003)
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

    if str(message.content).upper() == ("*PAUSE"):
        Player.pause()
        em = discord.Embed(colour=3447003)
        em = discord.Embed(title="Paused By " + str(message.author), icon_url=message.author.avatar_url , description=("Paused Song: " + Player.title), colour=3447003)
        em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
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
