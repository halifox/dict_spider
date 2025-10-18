import logging
from typing import Any

import scrapy
from scrapy.http import Response


class Spider(scrapy.Spider):
    name = "ip"

    def start_requests(self):
        # yield scrapy.Request("https://baidu.com", callback=self.parse)
        yield scrapy.Request("http://ip-api.com/line", callback=self.parse)
        # yield scrapy.Request("http://ipinfo.io/ip", callback=self.parse)
        # yield scrapy.Request("http://ifconfig.me", callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        logging.warn(response.text)
