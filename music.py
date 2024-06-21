import discord
import yt_dlp

FFMPEG_OPTIONS = {'options' : '-vn'}
YDL_OPTIONS = {'format' : 'bestaudio', 'noplaylist' : True}

queue = []

async def add_song(ctx,search):
    voice_channel = ctx.author.voice.channel

    # join voice
    if not ctx.voice_client:
        await voice_channel.connect()

    async with ctx.typing(): # show typing while processing
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url = info['url']
            title = info['title']
            queue.append((url,title))
            await ctx.send(f'🎼 **{title}** 次に再生します。Added to queue🎶')
    
    if not ctx.voice_client.is_playing():
        await play_song(ctx)


async def play_song(ctx):
    if queue:
        url,title = queue.pop(0)
        try:
            print(f'Preparing to play: {title}')
            source = await discord.FFmpegOpusAudio.from_probe(url,**FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda _:ctx.bot.loop.create_task(play_song(ctx)))
            await ctx.send(f'▶️ **{title}**再生中。Now playing.')
        except Exception as e:
            print(f'Error playing song: {e}')
    elif not ctx.voice_client.is_playing():
        await ctx.send('⏏️ 新曲追加お願いします。Music queue is empty!')
    

async def skip_song(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('⏭️ 曲スキップします。Song skipped.')


async def stop_song(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('⏹️ 再生停止です。Stopped music.')
