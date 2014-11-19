import asyncio


class UDPServ:
    def datagram_received(data, addr):
        print(data, addr)
    def error_received(exc):
        print(str(exc))


loop = asyncio.get_event_loop()
loop.run_until_complete(display_date(loop))
loop.close()
