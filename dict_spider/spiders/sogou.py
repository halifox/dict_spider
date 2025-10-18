import re
import scrapy


class SogouSpider(scrapy.Spider):
    name = "sogou"
    allowed_domains = ["pinyin.sogou.com"]
    start_urls = ["https://pinyin.sogou.com/dict/"]

    def parse(self, response):
        """
        解析一级分类（主分类）。

        1. 获取页面中所有一级分类节点。
        2. 提取分类名称、链接和分类ID。
        3. 生成一级分类的数据 yield。
        4. 对每个一级分类，发送请求到二级分类页面 parse_subcategory。

        参数:
        - response: scrapy 响应对象，包含一级分类页面的 HTML

        返回:
        - yield 分类字典或 scrapy.Request 请求对象
        """
        category_list = response.xpath("//*[contains(@class, 'dict_category_list_title')]")
        for category in category_list:
            category_name = category.xpath("./a/text()").get()
            category_href = category.xpath("./a/@href").get()
            category_id = re.search(r'/dict/cate/index/(\d+)', category_href).group(1)
            yield {
                'type': "category",
                'source': "sogou",
                'id': category_id,
                'name': category_name,
                'index': [category_id],
            }
            yield scrapy.Request(
                url='https://pinyin.sogou.com' + category_href,
                callback=self.parse_subcategory,
                cb_kwargs={"parent_index": [category_id]}
            )

    def parse_subcategory(self, response, parent_index):
        """
        解析二级分类及三级分类。

        1. 获取二级分类及其子分类的表格节点。
        2. 遍历每个 td 节点：
            - 获取城市列表类型的二级分类（citylist）
            - 获取普通二级分类
            - 获取三级分类
        3. 生成对应分类的 yield 数据。
        4. 对每个二级/三级分类，发送请求到分页页面 parse_pages。

        参数:
        - response: scrapy 响应对象，包含当前分类页面 HTML
        - parent_index: list, 父级分类的 id 列表，用于追溯分类层级

        返回:
        - yield 分类字典或 scrapy.Request 请求对象
        """
        td_list = response.xpath("//*[@class='cate_words_list']/tbody/tr/td")
        for td in td_list:
            # 城市列表二级分类
            for city in td.xpath(".//*[@class='citylist']"):
                name = city.xpath("./text()").get()
                href = city.xpath("./@href").get()
                id = re.search(r'/dict/cate/index/(\d+)', href).group(1)
                yield {
                    'type': "category",
                    'source': "sogou",
                    'id': id,
                    'name': name,
                    'index': [*parent_index, id],
                }
                yield scrapy.Request(
                    url='https://pinyin.sogou.com' + href,
                    callback=self.parse_pages,
                    cb_kwargs={"parent_index": [*parent_index, id]}
                )

        for td in td_list:
            # 普通二级分类
            subcategory_name = td.xpath("./div[1]/a/text()").get()
            subcategory_href = td.xpath("./div[1]/a/@href").get()
            subcategory_id = re.search(r'/dict/cate/index/(\d+)', subcategory_href).group(1)
            yield {
                'type': "category",
                'source': "sogou",
                'id': subcategory_id,
                'name': subcategory_name,
                'index': [*parent_index, subcategory_id],
            }

            # 三级分类
            for child_category in td.xpath(".//div[@class='cate_child_name']"):
                child_name = child_category.xpath("./a/text()").get()
                child_href = child_category.xpath("./a/@href").get()
                child_id = re.search(r'/dict/cate/index/(\d+)', child_href).group(1)
                yield {
                    'type': "category",
                    'source': "sogou",
                    'id': child_id,
                    'name': child_name,
                    'index': [*parent_index, subcategory_id, child_id],
                }
                yield scrapy.Request(
                    url='https://pinyin.sogou.com' + child_href,
                    callback=self.parse_pages,
                    cb_kwargs={"parent_index": [*parent_index, subcategory_id, child_id]}
                )

    def parse_pages(self, response, parent_index):
        """
        解析分页信息，获取当前分类的最大页码。

        1. 提取页面中所有分页链接。
        2. 使用正则匹配页码。
        3. 获取最大页码后，生成每一页的请求请求 parse_dict_detail。

        参数:
        - response: scrapy 响应对象，包含当前分类页面 HTML
        - parent_index: list, 父级分类 id，用于追溯层级

        返回:
        - yield scrapy.Request 请求对象
        """
        hrefs = response.xpath("//a/@href").getall()
        page_numbers = []

        for href in hrefs:
            match = re.search(r'/dict/cate/index/(\d+)/default/(\d+)', href)
            if match:
                page_numbers.append(int(match.group(2)))

        if page_numbers:
            max_page = max(page_numbers)
            for page in range(1, max_page + 1):
                yield scrapy.Request(
                    url=f'https://pinyin.sogou.com/dict/cate/index/{parent_index[-1]}/default/{page}',
                    callback=self.parse_dict_detail,
                    cb_kwargs={"parent_index": parent_index}
                )

    def parse_dict_detail(self, response, parent_index):
        """
        解析具体词条信息（词典条目）。

        提取每个词条的详细信息：
        - dict_name: 词条名称
        - dict_href: 词条详情页 URL
        - dict_id: 词条唯一 ID
        - example_word: 示例内容或用法
        - download_count: 下载次数
        - update_time: 最后更新时间

        参数:
        - response: scrapy 响应对象，包含词条列表页面 HTML
        - parent_index: list, 父级分类 id，用于追溯层级

        返回:
        - yield 词条信息字典
        """
        for detail in response.xpath("//*[contains(@class, 'dict_detail_block')]"):
            dict_name = detail.xpath(".//*[@class='detail_title']/a/text()").get()
            dict_href = detail.xpath(".//*[@class='detail_title']/a/@href").get()
            dict_id = re.search(r'/dict/detail/index/(\d+)', dict_href).group(1)
            example_word = detail.xpath("(.//*[@class='show_content'])[1]/text()").get()
            download_count = detail.xpath("(.//*[@class='show_content'])[2]/text()").get()
            update_time = detail.xpath("(.//*[@class='show_content'])[3]/text()").get()
            yield {
                'type': "dict",
                'source': "sogou",
                'id': dict_id,
                'name': dict_name,
                'href': 'https://pinyin.sogou.com' + dict_href,
                'example': example_word,
                'count': download_count,
                'time': update_time,
                'index': parent_index,
            }
