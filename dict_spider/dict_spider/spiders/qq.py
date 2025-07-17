import scrapy
from bs4 import BeautifulSoup
import re


class Spider(scrapy.Spider):
    name = "qq"
    allowed_domains = ["cdict.qq.pinyin.cn"]
    start_urls = ["https://cdict.qq.pinyin.cn/"]

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        for category_div in soup.find_all("div", class_="cikuCategory"):
            links = category_div.find_all("a")
            if not links:
                continue

            # 一级分类
            primary_link = links[0]
            primary_href = primary_link["href"]
            primary_id = re.search(r'cate_id=(\d+)', primary_href).group(1)
            yield {
                'dict_id': primary_id,
                'dict_pid': None,
                'dict_name': primary_link.text,
                'dict_innerid': None,
                'dict_time': None,
                'dict_downcount': None,
                'dict_exps': None,
                'dict_tiers': 1
            }

            # 二级分类
            for secondary_link in links[1:]:
                secondary_href = secondary_link["href"]
                dict_id = re.search(r'cate_id=(\d+)', secondary_href).group(1)
                dict_name = secondary_link.text
                yield {
                    'dict_id': dict_id,
                    'dict_pid': primary_id,
                    'dict_name': dict_name,
                    'dict_innerid': None,
                    'dict_time': None,
                    'dict_downcount': None,
                    'dict_exps': None,
                    'dict_tiers': 2,
                }
                url = f'https://cdict.qq.pinyin.cn/list?cate_id={dict_id}'
                yield scrapy.Request(url, callback=self.parse3, meta={'dict_id': dict_id, 'dict_name': dict_name})

    def parse3(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        if not 'page' in response.meta:
            match = re.search(r'共(\d+)页', response.text)
            max_page = match.group(1) if match else None
            if not max_page:
                max_page = 1
            else:
                max_page = int(max_page)
            for page in range(1, int(max_page) + 1):
                url = f'https://cdict.qq.pinyin.cn/list?cate_id={response.meta['dict_id']}&page={page}'
                yield scrapy.Request(url, callback=self.parse3, meta={
                    'dict_id': response.meta['dict_id'],
                    'dict_name': response.meta['dict_name'],
                    'page': page,
                })

        trs = soup.find_all("div", {"class": "summary"})
        for tr in trs:
            a = tr.find('a')
            href = a['href']
            dict_id = re.search('dict_id=([^&]+)&', href).group(1)
            url = f'https://cdict.qq.pinyin.cn/detail?dict_id={dict_id}'
            yield scrapy.Request(url, callback=self.parse_detail, meta={
                'dict_id': dict_id,
                'dict_pid': response.meta['dict_id'],
            })

    def parse_detail(self, response, **kwargs):
        dict_id = response.meta['dict_id']
        dict_pid = response.meta['dict_pid']
        soup = BeautifulSoup(response.text, 'html.parser')
        dict_name = soup.find('h3', class_='margin-top-left-10').get_text(strip=True)
        dict_type = soup.find_all('span')[0].get_text(strip=True)
        dict_time = soup.find_all('span')[2].get_text(strip=True)
        dict_count = soup.find_all('span')[3].get_text(strip=True)
        dict_downcount = soup.find_all('span')[5].get_text(strip=True)
        dict_exps = soup.find_all('p')[1].get_text(strip=True)
        yield {
            'dict_id': dict_id,
            'dict_pid': dict_pid,
            'dict_name': dict_name,
            'dict_innerid': dict_id,
            'dict_time': dict_time,
            'dict_downcount': dict_downcount,
            'dict_exps': dict_exps,
            'dict_tiers': 3
        }


def find_attr_recursive(self, soup, attr_name):
    tag = soup.find(attrs={attr_name: True})
    value = tag[attr_name] if tag else None
    return value
