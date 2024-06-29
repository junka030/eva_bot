import random
import requests
import json
import os
import discord
from easy_pil import Editor,load_image_async,Font

# test function
def get_response(user_input:str) -> str:
    # raise NotImplementedError('Missing code...')
    lowered: str = user_input.lower()

    if lowered == '':
        return '。。。？'
    else:
        return random.choice([
            'なに？','。。。','わかりません。','もう訓練の時間です。'
        ]) 
    
async def send_gif(ctx,apikey,search_term):
    lmt = 8 # limit 
    ckey = "dcbot"
    url = f"https://tenor.googleapis.com/v2/search?q={search_term}&key={apikey}&client_key={ckey}&limit={lmt}"
    r = requests.get(url) 
    idx = random.randint(0, 7)

    if r.status_code == 200:
        data = json.loads(r.content)
        await ctx.send(data['results'][idx]['url'])

    else:
        print("Failed to fetch GIFs from Tenor API.")
        await ctx.send("Can't fetch GIF >.<")

def get_pic_path(cname):

    mainfd = "pics"
    dirs = os.listdir(mainfd)

    for i in range(len(dirs)):

        if cname in dirs[i]: 
            subfd = os.path.join(mainfd,dirs[i])       
            imgs = os.listdir(subfd)
            rdmidx = random.randint(0,len(imgs)-1)

            filename = os.path.join(subfd,imgs[rdmidx])
    
    if not filename:
        filename = "pics\rei\24.jpg"

    return filename

async def send_charpic(interaction,cname):
    filename = get_pic_path(cname)
    await interaction.response.send_message(file=discord.File(filename))

# select menu for characters
class CharView(discord.ui.View):
    @discord.ui.select(
        placeholder = "Select a character!",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(
                label="綾波レイ Ayanami Rei",
                value='rei'
            ),
            discord.SelectOption(
                label="惣流・アスカ・ラングレー Soryu Asuka Langley",
                value='asuka'
            )
        ]
    )
    async def callback(self,select,interaction):
        await send_charpic(interaction,select.values[0])