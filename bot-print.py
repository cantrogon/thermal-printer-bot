import discord
from discord import app_commands
from print_requester import print_random_by_query, print_random_creature_by_cmc, print_card_by_name

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DISCORD_TOKEN = 'DISCORD_TOKEN_HERE'

def handle_print(action, text):
    if action == "cmc":
        print_random_creature_by_cmc(text)
        return f"Printed random creature of cmc {text}"
    elif action == "random":
        print_random_by_query(text)
        return f"Printed random card with query {text}"
    elif action == "name":
        print_card_by_name(text)
        return f"Printed card with name {text}"
    else:
        return None

@client.event
async def on_ready():
    print(f'Bot is online as {client.user}')
    await tree.sync()
    print("Commands synced!")

# Slash command
@tree.command(name="print", description="Prints a card.")
@app_commands.describe(
    action="cmc, random, name", 
    query="The query string"
)
async def print_card(interaction: discord.Interaction, action: str, query: str):
    result = handle_print(action.lower(), query)
    if result:
        await interaction.response.send_message(result)
    else:
        await interaction.response.send_message("Unknown action.")

client.run(DISCORD_TOKEN)
