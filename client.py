from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from chat import get_response

# load token
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
# print(TOKEN)

# setup
intents: Intents = Intents.default() # varname: vartype = assignment
intents.message_content = True

client: Client = Client(intents=intents)

# message
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("(Empty message, intents not enabled)")
        return
    
    # trigger private inbox
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    
    try:
        response: str = get_response(user_message)
        # print("responding...")
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(f"error: {e}")

# bot startup
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# handle incoming message
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user: # message by bot
        return 
    
    username: str = str(message.author) # channel message username
    user_message: str = message.content # message content
    channel: str = str(message.channel)

    # log msg
    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

# main entry point
def main() -> None:
    try:
        client.run(token=TOKEN)
    except KeyboardInterrupt:
        print("Entry plug ejected...")
    


if __name__ == '__main__':
    main()