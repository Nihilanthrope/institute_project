import os
import asyncio
import discord
from dotenv import load_dotenv
from bot import ROLE_PERMISSION_POLICY, CATEGORY_ACCESS_POLICY, GAME_ROLES, GUILD_ID

load_dotenv()
intents = discord.Intents.default()
intents.guilds = True

async def main():
    client = discord.Client(intents=intents)
    done = asyncio.Event()
    result = {"ok": False}

    @client.event
    async def on_ready():
        guild = client.get_guild(GUILD_ID)
        if not guild:
            print("VERIFY_FAIL guild missing")
            await client.close()
            return
        roles = {r.name: r for r in guild.roles}
        failures = []
        for name, expected in ROLE_PERMISSION_POLICY.items():
            role = roles.get(name)
            if not role:
                failures.append(f"missing role: {name}")
                continue
            actual = role.permissions.value
            if actual != expected.value:
                failures.append(f"role permissions mismatch: {name}")
        for category_name, allowed in CATEGORY_ACCESS_POLICY.items():
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                failures.append(f"missing category: {category_name}")
                continue
            if category.overwrites_for(guild.default_role).view_channel is not False:
                failures.append(f"@everyone can view: {category_name}")
            for role_name in allowed:
                role = roles.get(role_name)
                if role and category.overwrites_for(role).view_channel is not True:
                    failures.append(f"missing access: {category_name} -> {role_name}")
        print(f"LIVE_COUNTS roles={len(guild.roles)} channels={len(guild.channels)} categories={len(guild.categories)}")
        if failures:
            print("VERIFY_FAIL")
            print("\n".join(failures))
        else:
            print("VERIFY_PASS strict role permissions + restricted category access")
            result["ok"] = True
        await client.close()

    await client.start(os.getenv("DISCORD_TOKEN"))
    return result["ok"]

if __name__ == "__main__":
    asyncio.run(main())
