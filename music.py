import discord
import yt_dlp
import asyncio
from discord.ext import commands

FFMPEG_OPTIONS = {'options' : '-vn'}
YDL_OPTIONS = {
    'format': 'bestaudio',
    'noplaylist': True,
    'cookiefile': 'data/seasalt_chocchip_cookie.txt',  # Add this line
    'default_search': 'ytsearch'
}
CHOICE_TIMEOUT = 10  # seconds

queue = []
pending_choices = {}


async def add_song(ctx, search):
    voice_channel = ctx.author.voice.channel

    if not ctx.voice_client:
        await voice_channel.connect()

    async with ctx.typing():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                await ctx.send("🔄️ 曲検索中。。。Querying for songs...")
                # Refined search query: Only look for videos
                info = ydl.extract_info(f"ytsearch5:{search} videos", download=False)

                if 'entries' in info and info['entries']:
                    # Filter out only video entries (ignore channel, playlist, or mix)
                    # videos = [entry for entry in info['entries'] if entry.get('_type') == 'video']
                    # print("Filtered videos:", videos)

                    # print("Entries found:", info['entries'])
                    videos = info['entries'] # no filter
        
                    if not videos:
                        await ctx.send("⚠️ 再生可能な動画が見つかりませんでした。No playable video found.")
                        return
                                        
                    # Limit to a smaller number of results (e.g., top 5)
                    videos = videos[:5]

                    # Prepare the result message with choices
                    msg = "**🔎 検索結果 / Search Results:**\n"
                    for idx, video in enumerate(videos, start=1):
                        msg += f"{idx}. {video.get('title', 'Unknown Title')}\n"
                    msg += f"\n数字を送信して選んでください! Send the number of your choice! (Timeout: {CHOICE_TIMEOUT}s)"

                    await ctx.send(msg)

                    pending_choices[ctx.author.id] = {
                        'videos': videos,
                        'ctx': ctx
                    }

                    # Wait for user input
                    def check(m):
                        # print(f"Checking message: {m.content}")
                        return (
                            m.author == ctx.author and 
                            m.channel == ctx.channel and
                            m.content.isdigit() and 
                            1 <= int(m.content) <= len(videos)
                        )

                    try:
                        print("Waiting for user response of song choice...")
                        response = await asyncio.wait_for(
                            ctx.bot.wait_for('message', check=check),
                            timeout=CHOICE_TIMEOUT
                        )
                        
                        # Ensure response is valid and user has sent something
                        if response is None:
                            raise TimeoutError("No response received within the timeout period.")
                        
                        # print("User response:", response.content)

                        choice = int(response.content) - 1
                        selected_video = videos[choice]

                    except asyncio.TimeoutError:
                        # Handle the timeout case by picking the first video
                        selected_video = videos[0]
                        await ctx.send(f"⏰ タイムアウトしました! 最初の曲を再生します。Timeout! Picking the first song...")

                    except ValueError:
                        # Handle invalid input (non-digit or out of range)
                        await ctx.send(f"⚠️ Invalid input! Please send a number between 1 and {len(videos)}.")

                    except Exception as e:
                        print(f"Exception occurred: {str(e)}")
                        await ctx.send(f"⚠️ エラー発生。Error during selection.\n")
                        return
                    
                    # Extract video URL and title
                    url = selected_video.get('url')
                    title = selected_video.get('title', 'Unknown Title')

                    if not url:
                        await ctx.send("⚠️ URLを取得できませんでした。Unable to extract video URL.")
                        return

                    # Add the song to the queue
                    queue.append((url, title))
                    await ctx.send(f'🎼 **{title}** をキューに追加しました!Added to queue 🎶')

                    # If no song is currently playing, start the song
                    if not ctx.voice_client.is_playing():
                        await play_song(ctx)

                else:
                    await ctx.send("⚠️ 検索結果が見つかりませんでした。No results found.")
                    return

            except Exception as e:
                await ctx.send(f"⚠️ エラー発生。Error during search.\n```{e}```")
                return


async def play_song(ctx):
    if queue:
        url, title = queue.pop(0)  # Get the next song
        try:
            print(f'Preparing to play: {title}')
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            # Play the song and use `after` to call `play_next_song` once the current song finishes
            ctx.voice_client.play(source, after=lambda _: asyncio.create_task(play_next_song(ctx)))
            await ctx.send(f'▶️ **{title}** 再生中。Now playing.')
        except Exception as e:
            print(f'Error playing song: {e}')
            await ctx.send(f"⚠️ エラー発生。Error playing song: {e}")
    else:
        await ctx.send('⏏️ 新曲追加お願いします。Music queue is empty!')


async def play_next_song(ctx):
    # This function is called once a song finishes playing (from the `after` callback)
    if queue:
        await play_song(ctx)  # Play the next song
    else:
        await ctx.send('⏏️ 曲が終了しました。The queue is now empty.')
    

async def skip_song(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('⏭️ 曲スキップします。Song skipped.')


async def stop_song(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('⏹️ 再生停止です。Stopped music.')
