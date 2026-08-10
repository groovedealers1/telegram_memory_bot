import asyncio
import src


async def main():
    task_1 = asyncio.create_task(src.start_bot())
    task_2 = asyncio.create_task(src.send_message())
    await task_1
    await task_2

if __name__ == '__main__':
    asyncio.run(main())
