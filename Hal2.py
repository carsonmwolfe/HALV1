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
START_TIME = datetime.datetime.now()
profooter=""
EMBEDCOLOR = 3447033



ytdl_format_options = {
    'format': 'bestaudio/best',
    'download': False
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'options': '-vn'
}

class music_handler():
    def __init__(self,server,player,channel):
        self.server = server
        self.channel = channel
        server.voice_client.encoder_options(sample_rate=48000,channels=2)
        player.start()
        self.player=player
        self.paused = False
        self.message = None
        self.starttime = datetime.now()
        self.duration = player.duration
        self.title = player.title
        self.link = player.url
        if self.player.is_live == False:
             if self.player.is_live == False:
                mins=int(self.duration/60)
                seconds=int(self.duration-(mins*60))
                hours=int(mins/60)
                if hours > 0:
                    mins=mins-(hours*60)
                    if len(str(mins))==1:
                        mins="0"+str(mins)
                    if len(str(seconds)) == 1:
                        self.length=str(hours)+":"+str(mins)+":"+"0"+str(seconds)
                    else:
                        self.length=str(hours)+":"+str(mins)+":"+str(seconds)
                else:
                    if len(str(seconds)) == 1:
                        self.length=str(mins)+":"+"0"+str(seconds)
                    else:
                        self.length=str(mins)+":"+str(seconds)
        else:
            self.length = "Currently Streaming"
        self.desc = ("["+self.title+"]("+self.link+")\n**Progress:**: `0:00 / "+self.length+"`\n**Volume:** "+str(int(self.player.volume*100)))
        self.em = discord.Embed(description=self.desc,colour=EMBEDCOLOR)
        self.em.set_author(name = "Music", icon_url="http://www.charbase.com/images/glyph/9835")
        self.footer=profooter
        self.em.set_footer(text=profooter)
        self.is_playing=True
        self.pausedatetime=None
        self.pausetime=None
        client.loop.create_task(self.update_loop())

    async def update_loop(self):
        while self.is_playing:
            if self.player.is_playing():
                self.is_playing=True
            elif self.player.is_playing==False and self.paused==False:
                self.is_playing=False
            import datetime
            queuelist="\nNo songs in queue"
            if len(serverinfo[self.server].queue)>1:
                queuelist=""
                i=0
                for song in serverinfo[self.server].queue[1:]:
                    i=i+1
                    if len(song)>2:
                        queuelist=queuelist+"\n`#{0}` {1}".format(i,song)
                    else:
                        queuelist=queuelist+"\n`#{0}` {1}".format(i,"["+(''.join(song[0]))+"]("+song[1]+")")
            if self.paused:
                self.pausetime=datetime.datetime.now()-self.pausedatetime
            if self.pausetime==None:
                c = datetime.datetime.now()-self.starttime
            else:
                c = datetime.datetime.now()-(self.starttime+datetime.timedelta(seconds=self.pausetime.seconds))
            if self.paused == False:
                progress = divmod(c.days * 86400 + c.seconds, 60)
                self.minutedelta=str(progress).split('(')[1].split(')')[0].split(',')[0]
                self.seconddelta=str(progress).split('(')[1].split(')')[0].split(', ')[1]
                if len(str(self.seconddelta)) == 1:
                    self.seconddelta='0'+str(self.seconddelta)
                self.hours=int(int(self.minutedelta)/60)
                percent=int(18*(((int(self.hours)*3600)+(int(self.minutedelta)*60)+int(self.seconddelta))/int(self.duration)))+1
                if self.player.is_live == False:
                    self.bar=("▣"*percent)+"▢"*(18-percent)
                else:
                    self.bar="▣"*18
            pauseStr=""
            if self.paused:
                pauseStr=" (paused)"
            if self.hours>0:
                self.minutedelta=int(self.minutedelta)-(hours*60)
                if len(str(self.minutedelta))==1:
                    self.minutedelta="0"+str(self.minutedelta)
                else:
                    self.minutedelta=str(self.minutedelta)
                self.em=discord.Embed(description = self.desc.split('**Progress:**')[0]+'**Volume:** '+str(int(self.player.volume*100))+'%'+'\n**Progress:** `'+str(self.hours)+":"+str(self.minutedelta)+':'+str(self.seconddelta)+' / '+self.length+'`'+pauseStr+'\n'+self.bar+'\n**Queue:**'+queuelist,colour=EMBEDCOLOR)
            else:
                self.em=discord.Embed(description = self.desc.split('**Progress:**')[0]+'**Volume:** '+str(int(self.player.volume*100))+'%'+'\n**Progress:** `'+str(self.minutedelta)+':'+str(self.seconddelta)+' / '+self.length+'`'+pauseStr+'\n'+self.bar+'\n**Queue:**'+queuelist,colour=EMBEDCOLOR)
            self.em.set_footer(text=self.footer)
            self.em.set_author(name = "Music", icon_url="http://www.charbase.com/images/glyph/9835")
            if (self.is_playing == False or c.seconds >= self.duration) and self.player.is_live == False:
                self.player.stop()
                em=discord.Embed(description = "["+self.title+"]("+self.link+")\n**Song Ended**", colour=EMBEDCOLOR)
                em.set_author(name = "Music", icon_url="http://www.charbase.com/images/glyph/9835")
                await client.edit_message(self.message,embed=em)
                serverinfo[self.server].queue.remove(serverinfo[self.server].queue[0])
                self.is_playing=False
                serverinfo[self.server].mHandler=None
                serverinfo[self.server].end_time=datetime.datetime.now()
            else:
                if self.message != None:
                    try:
                        await client.edit_message(self.message,embed=self.em)
                    except:
                        self.message=None
                if self.message==None:
                    self.message=await client.send_message(self.channel,embed=self.em)
                else:
                    await client.edit_message(self.message,embed=self.em)
            await asyncio.sleep(2)
            
            

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
        await message.channel.send(message.channel, embed = em)

    if str(message.content).upper() == ("*LEAVE"):
        await message.guild.voice_client.disconnect()
        em = discord.Embed(colour=3447003)
        em.set_author(name="Hal has been disconnect from the voice channel")
        Player = None
        await message.channel.send(message.channel, embed=em)

    if str(message.content).upper().upper()==("*MOVE"):
        await Member.edit()(user,channel)
        em = discord.Embed(colour=3447003)
        em.set_author(name = "Hal Has moved channels" + "\n" + "Note: If Hal Moves During A Song, The Song Will Stop Playing ")
        await message.channel.send(message.channel, embed=em)

    if str(message.content).upper().startswith("*VOLUME|"):
        Player.volume
        total= int(str(message.content).split('|')[1])
        Player.volume=total/100
        em = discord.Embed(colour=3447003)
        em.set_author(name="Music Volume has been changed to {0}".format(str(total))+"%." )
        await message.channel.send(message.channel, embed=em)
        
    if str(message.content).upper().startswith("*PLAY|"):
       
        if Player!=None:
            if message.guild.voice_client.is_playing():
                message.guild.voice_client.stop()
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
                while message.guild.voice_client == None:
                    await message.guild.voice_client.play(Player)
                Player = await YTDLSource.from_url(link,loop = client.loop)
                em = discord.Embed(title=" Playing: " + Player.title, description=('Volume:  {0}'.format(str(Player.volume*100))+"%." +"\n" +  'Duration: '+str(int(round(Player.duration/60)))+(' Minutes \nLink: '+ link)), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await message.channel.send(message.channel, embed=em)
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
                em = discord.Embed(title=" Playing: " + Player.title, description=('Volume:  {0}'.format(int(Player.volume*100))+"%." + "\n" + 'Duration: '+str(int(round(Player.duration/60)))+(' Minutes \nLink: '+ link)), colour=3447003)
                em.set_author(name="Selected By: " + str(message.author),icon_url=message.author.avatar_url)
                em.set_footer(text="Hal | {:%b, %d %Y}".format(today))
                await message.channel.send(message.channel, embed=em)
        except IndexError:
            await message.channel.send ("Could not find this video on YouTube.")
            if(Player.is_playing == False):
                em= discord.Embed(description = Player.title +link+ "\n" + "**Song Has Ended**", colour = 3447003)
                em.set_author(name = "Music", icon_url=message.author.avatar_url)
                await message.channel.send(message.channel, embed=em)

                                  
client.loop.run_until_complete(client.start(TokenDoc.token))
