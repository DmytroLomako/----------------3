from modules import *
import aiogram

async def main():
    await dispatcher.start_polling(bot)
if __name__ == '__main__':
    aiogram._asyncio.run(main())