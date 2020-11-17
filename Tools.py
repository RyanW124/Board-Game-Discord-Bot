async def senddm(user, content, embed=False):
    try:
        channel = await user.create_dm()
        if embed:
            await channel.send(embed=content)
        else:
            await channel.send(content)
    except:
        pass