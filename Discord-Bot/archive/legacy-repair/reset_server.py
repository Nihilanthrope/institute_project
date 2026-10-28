import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("Discord token not found in .env")

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Connected as {client.user}")

    for guild in client.guilds:
        print(f"\nRESETTING: {guild.name}")

        # Delete all channels
        for channel in list(guild.channels):
            try:
                await channel.delete(reason="Rupzha fresh server reset")
                print(f"Deleted channel: {channel.name}")
            except Exception as e:
                print(f"Could not delete {channel.name}: {e}")

        # Delete all custom roles
        # @everyone and Discord-managed roles stay.
        for role in sorted(list(guild.roles), key=lambda r: r.position, reverse=True):
            if role.is_default() or role.managed:
                continue

            try:
                await role.delete(reason="Rupzha fresh server reset")
                print(f"Deleted role: {role.name}")
            except Exception as e:
                print(f"Could not delete role {role.name}: {e}")

        print("RESET COMPLETE")

    await client.close()

client.run(TOKEN)
