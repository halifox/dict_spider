import scrapy
from bs4 import BeautifulSoup
import re


class Spider(scrapy.Spider):
    name = "sougo"
    allowed_domains = ["pinyin.sogou.com"]
    start_urls = ["https://pinyin.sogou.com/dict/"]

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        category_list = soup.select('.dict_category_list_title')
        for category in category_list:
            a = category.select_one('a')
            href = a.get('href')
            dict_id = re.search(r'(\d+)', href).group(1)
            dict_name = a.text
            yield {
                'dict_id': dict_id,
                'dict_pid': None,
                'dict_name': dict_name,
                'dict_innerid': None,
                'dict_time': None,
                'dict_downcount': None,
                'dict_exps': None,
                'dict_tiers': 1
            }
            url = f'https://pinyin.sogou.com/dict/cate/index/{dict_id}'
            yield scrapy.Request(url, callback=self.parse2, meta={'dict_id': dict_id, 'dict_name': dict_name})

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('tr')
        trs = table.find_all('td', recursive=False)
        for tr in trs:
            a = tr.find("a")
            href = a['href']
            dict_id = re.search(r'/dict/cate/index/(\d+)', href).group(1)
            dict_name = a.text
            yield {
                'dict_id': dict_id,
                'dict_pid': response.meta['dict_id'],
                'dict_name': dict_name,
                'dict_innerid': None,
                'dict_time': None,
                'dict_downcount': None,
                'dict_exps': None,
                'dict_tiers': 2
            }

            table0 = tr.find('tr')
            if not table0:
                url = f'https://pinyin.sogou.com/dict/cate/index/{dict_id}'
                yield scrapy.Request(url, callback=self.parse3,
                                     meta={'dict_id': dict_id, 'dict_name': dict_name})
                continue
            dict_pid = dict_id
            trs0 = table0.find_all('td', recursive=False)
            for tr0 in trs0:
                a0 = tr0.find("a")
                href0 = a0['href']
                dict_id = re.search(r'/dict/cate/index/(\d+)', href0).group(1)
                dict_name = a0.text
                yield {
                    'dict_id': dict_id,
                    'dict_pid': dict_pid,
                    'dict_name': dict_name,
                    'dict_innerid': None,
                    'dict_time': None,
                    'dict_downcount': None,
                    'dict_exps': None,
                    'dict_tiers': 3
                }
                url = f'https://pinyin.sogou.com/dict/cate/index/{dict_id}'
                yield scrapy.Request(url, callback=self.parse3,
                                     meta={'dict_id': dict_id, 'dict_name': dict_name})

    def parse3(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')

        if not 'page' in response.meta:
            max_page = 1
            for a in soup.find('div', {'id': 'dict_page_list'}).find_all('a'):
                href = a.get('href')
                if href:
                    search = re.search(r'/default/(\d+)', href)
                    if search:
                        page = search.group(1)
                        if int(page) > max_page:
                            max_page = int(page)
            for page in range(1, int(max_page) + 1):
                url = f'https://pinyin.sogou.com/dict/cate/index/{response.meta['dict_id']}/default/{page}'
                yield scrapy.Request(url, callback=self.parse3, meta={
                    'dict_id': response.meta['dict_id'],
                    'dict_name': response.meta['dict_name'],
                    'page': page,
                })

        dict_detail_blocks = soup.find_all('div', class_='dict_detail_block')
        for dict_detail_block in dict_detail_blocks:
            detail_title = dict_detail_block.select_one('.detail_title')
            show_connects = dict_detail_block.select('.show_content')
            href = detail_title.find('a')['href']
            dict_id = re.search(r'(\d+)', href).group(1)
            dict_name = detail_title.text
            dict_exps = show_connects[0].text
            dict_downcount = show_connects[1].text
            dict_time = show_connects[2].text
            yield {
                'dict_id': dict_id,
                'dict_pid': response.meta['dict_id'],
                'dict_name': dict_name,
                'dict_innerid': None,
                'dict_time': dict_time,
                'dict_downcount': dict_downcount,
                'dict_exps': dict_exps,
                'dict_tiers': 4
            }
