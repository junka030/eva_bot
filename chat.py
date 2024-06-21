import random
import requests
import json

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