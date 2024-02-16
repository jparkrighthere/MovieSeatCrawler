import telegram
import asyncio

bot = telegram.Bot(token = '6788564300:AAHX3yeXXWoAxOdN90T3VHcR7v6WxlxbqZE')

async def getUpdate() :
    msg=await bot.getUpdates()
    for data in msg :
        print(data)

asyncio.run(getUpdate())