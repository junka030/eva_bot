import discord
import requests
import json

FLASK_API_URL = 'http://127.0.0.1:5000/questions'

with open('config.json') as f:
    config = json.load(f)

gifO = config['correct_gif_url']
gifX = config['wrong_gif_url']

# button menu for quiz
class QuizView(discord.ui.View):
    def __init__(self,question_id,choices):
        super().__init__()
        self.question_id = question_id
        self.value = None
        self.gif = None

        for choice in choices:
            self.add_item(discord.ui.Button(label=choice['text'], custom_id=str(choice['id']), style=discord.ButtonStyle.blurple))
        
        self.add_item(discord.ui.Button(label="Quit", custom_id="quit", style=discord.ButtonStyle.red))


    async def interaction_check(self, interaction: discord.Interaction):

        if interaction.data['custom_id'] == "quit":
            await interaction.response.send_message("Quiz ended.")
            self.stop()  # Stop the view, ending interaction
            return
        
        choice_id = int(interaction.data['custom_id'])
        api_url = f"{FLASK_API_URL}/{self.question_id}/choices/{choice_id}"
        response = requests.get(api_url)
        data = response.json()
        
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.custom_id == str(choice_id):
                if data['is_correct']:
                    item.emoji = '⭕'  
                    item.style = discord.ButtonStyle.green
                    self.gif = gifO
                else:
                    item.emoji = '✖️'  
                    item.style = discord.ButtonStyle.red
                    self.gif = gifX
            item.disabled = True

        gif_url = gifO if data['is_correct'] else gifX
        embed = discord.Embed()
        embed.set_image(url=gif_url)
        # if data['is_correct']:
        #     await interaction.response.send_message("Correct!")
        # else:
        #     await interaction.response.send_message("Incorrect!")
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=embed)






    # @discord.ui.button(label="ans A",style=discord.ButtonStyle.blurple,emoji="🦜")
    # async def choice1(self,button:discord.ui.Button,interaction:discord.Interaction):
    #     await interaction.response.send_message("chosen A!")

    # @discord.ui.button(label="ans B",style=discord.ButtonStyle.blurple,emoji="🐥")
    # async def choice2(self,button:discord.ui.Button,interaction:discord.Interaction):
    #     await interaction.response.send_message("chosen B!")

    # @discord.ui.button(label="ans C",style=discord.ButtonStyle.blurple,emoji="🐦‍⬛")
    # async def choice3(self,button:discord.ui.Button,interaction:discord.Interaction):
    #     await interaction.response.send_message("chosen C!")

    # @discord.ui.button(label="ans D",style=discord.ButtonStyle.blurple,emoji="🦩")
    # async def choice4(self,button:discord.ui.Button,interaction:discord.Interaction):
    #     await interaction.response.send_message("chosen D!")

