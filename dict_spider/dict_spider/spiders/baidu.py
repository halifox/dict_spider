import scrapy
from bs4 import BeautifulSoup
import re


class Spider(scrapy.Spider):
    name = "baidu"
    allowed_domains = ["shurufa.baidu.com"]
    start_urls = ["https://shurufa.baidu.com/dict.html"]

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        category_list = soup.find_all('a', attrs={'data-stats': 'webDictPage.dictSort.category1'})
        for category in category_list:
            href = category.get('href')
            dict_id = re.search(r'cid=(\d+)', href).group(1)
            span = category.find_all('span')[1]
            dict_name = span.text
            url = f'https://shurufa.baidu.com/dict_list?cid={dict_id}'
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
            yield scrapy.Request(url, callback=self.parse2, meta={'dict_id': dict_id, 'dict_name': dict_name})

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        tag_contain = soup.find('div', class_='tag_contain')
        if response.meta['dict_id'] == '157':
            category_list = tag_contain.find_all('a', attrs={'data-stats': 'webDictListPage.category1'})
        else:
            category_list = tag_contain.find_all('a', attrs={'data-stats': 'webDictListPage.category2'})

        for category in category_list:
            dict_id = category.get('cid')
            dict_name = category.get_text(strip=True)
            url = f'https://shurufa.baidu.com/dict_list?cid={dict_id}'
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
            yield scrapy.Request(url, callback=self.parse3, meta={'dict_id': dict_id, 'dict_name': dict_name})

    def parse3(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'html.parser')
        if not 'page' in response.meta:
            max_page = self.find_attr_recursive(soup, 'maxpage')
            if not max_page:
                max_page = 1
            else:
                max_page = int(max_page)
            for page in range(1, int(max_page) + 1):
                url = f'https://shurufa.baidu.com/dict_list?cid={response.meta['dict_id']}&page={page}'
                yield scrapy.Request(url, callback=self.parse3, meta={
                    'dict_id': response.meta['dict_id'],
                    'dict_name': response.meta['dict_name'],
                    'page': page,
                })

        dict_list_info = soup.find('div', class_='dict-list-info')
        trs = dict_list_info.find_all('tr')
        for tr in trs:
            dict_id = self.find_attr_recursive(tr, 'dict-id')
            dict_name = self.find_attr_recursive(tr, 'dict-name')
            dict_innerid = self.find_attr_recursive(tr, 'dict-innerid')
            dict_time = tr.find('span', class_='dict-time').get_text(strip=True)
            dict_downcount = tr.find('span', class_='dict-downcount').get_text(strip=True)
            dict_exps = [exps.get_text(strip=True) for exps in tr.find_all('span', class_='exps')]
            yield {
                'dict_id': dict_id,
                'dict_pid': response.meta['dict_id'],
                'dict_name': dict_name,
                'dict_innerid': dict_innerid,
                'dict_time': dict_time,
                'dict_downcount': dict_downcount,
                'dict_exps': dict_exps,
                'dict_tiers': 3
            }

    def find_attr_recursive(self, soup, attr_name):
        tag = soup.find(attrs={attr_name: True})
        value = tag[attr_name] if tag else None
        return value
