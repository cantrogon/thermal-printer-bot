import discord
from discord import app_commands
from print_requester import print_random_by_query, print_random_creature_by_cmc, print_card_by_name
from printer_main import print_request

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

with open('token.txt', 'r') as file:
    DISCORD_TOKEN = file.read()

def handle_print(action, text):
    if action == "cmc":
        res = print_random_creature_by_cmc(text)
        if res is None: return "Unable to print."
        return f"Printed random creature of mana value \"{text}\"."
    elif action == "random":
        res = print_random_by_query(text)
        if res is None: return "Unable to print."
        return f"Printed random card with query \"{text}\"."
    elif action == "name":
        res = print_card_by_name(text)
        if res is None: return "Unable to print."
        return f"Printed card with name \"{text}\"."
    else:
        return None

@client.event
async def on_ready():
    print(f'Bot is online as {client.user}')
    await tree.sync()
    print("Commands synced!")


@tree.command(name="print", description="Prints a card")
@app_commands.describe(
    action="cmc, random, name", 
    query="The query string"
)
async def print_card(interaction: discord.Interaction, action: str, query: str):
    result = handle_print(action.lower(), query)
    if result:
        await interaction.response.send_message(result)
    else:
        await interaction.response.send_message("Unknown action.", ephemeral=True)


def print_image(image):
    print_request(image, print_type="image")


@tree.command(name="print-image", description="Prints an image")
@app_commands.describe(image="Print an image")
async def sendimage(interaction: discord.Interaction, image: discord.Attachment):
    if image.content_type.startswith("image/"):
        image_data = await image.read()
        print_image(image_data)
        await interaction.response.send_message("Printed image!")
        # await interaction.followup.send(file=await image.to_file())
    else:
        await interaction.response.send_message("Please upload a valid image file.", ephemeral=True)


# def handle_print_special(action):
#     if action == "booster":
#         for _ in range(15):
#             print_random()
#         return "Printed booster pack!"


# @tree.command(name="print-special", description="Prints special")
# @app_commands.describe(
#     action="booster"
# )
# async def print_card(interaction: discord.Interaction, action: str):
#     result = handle_print_special(action.lower())
#     if result:
#         await interaction.response.send_message(result)
#     else:
#         await interaction.response.send_message("Unknown action.", ephemeral=True)



client.run(DISCORD_TOKEN)
