import asyncio

# ----------------------------------------------------------------------------
async def run1():
    while True:
        print("RUN1")
        await True


# ----------------------------------------------------------------------------
async def run2():
    while True:
        print("RUN: 2")
        await asyncio.sleep(0.01)


loop = asyncio.get_event_loop()
asyncio.ensure_future(run1())
asyncio.ensure_future(run2())
loop.run_forever()
