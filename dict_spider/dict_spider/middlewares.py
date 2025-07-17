import asyncio
import random
from twisted.internet import task, reactor
from scrapy import signals
import requests
import os
import pathlib
from dotenv import load_dotenv

env_path = pathlib.Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class ProxyMiddleware:
    def __init__(self):
        self.result = []
        self.loop = asyncio.get_event_loop()

    def process_request(self, request, spider):
        if self.result:
            proxy = random.choice(self.result)
            request.meta['proxy'] = f'http://{proxy}'

    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        crawler.signals.connect(mw.spider_opened, signals.spider_opened)
        crawler.signals.connect(mw.spider_closed, signals.spider_closed)
        return mw

    async def delayed_task(self, line: str):
        proxy, t = line.split(',')[0], int(line.split(',')[1])
        self.result.append(proxy)
        await asyncio.sleep(t)
        if proxy in self.result:
            self.result.remove(proxy)

    def fetch_and_schedule(self):
        proxy_pool_url = os.getenv("PROXY_POOL_URL")
        resp = requests.get(proxy_pool_url)
        if resp.status_code == 200:
            for line in resp.text.splitlines():
                asyncio.run_coroutine_threadsafe(self.delayed_task(line), self.loop)

    def look(self):
        with open("proxy_pool.txt", "w", encoding="utf-8") as f:
            for proxy in self.result:
                f.write(f"{proxy}\n")
            f.flush()
            os.fsync(f.fileno())

    def spider_opened(self, spider):
        self.task_loop = task.LoopingCall(self.fetch_and_schedule)
        self.task_loop.start(20)
        self.look_loop = task.LoopingCall(self.look)
        self.look_loop.start(10)

    def spider_closed(self, spider, reason):
        if hasattr(self, 'task_loop') and self.task_loop.running:
            self.task_loop.stop()
        if hasattr(self, 'look_loop') and self.look_loop.running:
            self.look_loop.stop()
