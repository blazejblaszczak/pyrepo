import asyncio
import aiohttp


async def fetch_url(session, url):
    async with session.get(url) as response:
        print(f"Response from {url}: {response.status}")
        return await response.text()
    
async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        await asyncio.gather(*tasks)


urls = ['http://example.com', 'https://api.github.com', 'https://www.python.org']
asyncio.run(main(urls))


""" CLIENT
import asyncio


async def tcp_client(request):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print(f"Sending {request}")
    writer.write(request.encode())
    response = await reader.read(1024)
    print(f"Received: {response.decode()}")
    writer.close()
    await writer.wait_closed()

    
asyncio.run(tcp_client("Hello, Async Programming World!"))
"""

"""SERVER
import asyncio


async def process_request(data):
    await asyncio.sleep(1) # simulate IO operation
    return data[::-1] 

    
async def handle_client(reader, writer):
    data = await reader.read(1024)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print(f"Received {message} from {addr}")
    response = await process_request(message)
    print(f"Sending: {response} to {addr}")
    writer.write(response.encode())
    await writer.drain()
    writer.close()

    
async def server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f"serving on port {addr}")
    async with server:
        await server.serve_forever()

        
asyncio.run(server()) 
"""
