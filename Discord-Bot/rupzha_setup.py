async def get_or_create_category(guild, name, overwrites=None):
    category = discord.utils.get(guild.categories, name=name)

    if category:
        return category

    return await guild.create_category(
        name,
        overwrites=overwrites or {},
        reason="Rupzha Core server setup"
    )
