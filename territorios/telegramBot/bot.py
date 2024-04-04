import asyncio
import telegram
# 334575560
async def main():
    bot = telegram.Bot("5937302183:AAHxqvoy9UjAIVIMlDUp6J7ny6y3D8X9brw")
    async with bot:
        await bot.send_message(text='Hi John!', chat_id=334575560)

if __name__ == '__main__':
    asyncio.run(main())
