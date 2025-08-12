from aiohttp import web


async def run_server(bind, path):
    runner = web.AppRunner(app)
    await runner.setup()
    for host in bind:
        site = web.TCPSite(runner, host, 80)
    await site.start()
