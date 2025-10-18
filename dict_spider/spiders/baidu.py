import re
import scrapy


class SogouSpider(scrapy.Spider):
    name = "baidu"
    allowed_domains = ["shurufa.baidu.com"]
    start_urls = ["https://shurufa.baidu.com/dict.html"]

    def parse(self, response):
        """
        解析一级分类及其子分类。

        功能：
        1. 获取首页的一级分类列表。
        2. 提取一级分类的名称、链接和分类ID。
        3. 生成一级分类的数据 yield。
        4. 获取二级分类（子分类），生成数据并发送请求到分页解析 parse_pages。

        参数：
        - response: scrapy 的 Response 对象，包含首页 HTML

        返回：
        - yield 分类字典或 scrapy.Request 请求对象
        """
        category_list = response.xpath("//*[contains(@class, 'dict_category')]//li")
        for category in category_list:
            # 一级分类信息
            category_name = category.xpath("./p/a/span[2]/text()").get()
            category_href = category.xpath("./p/a/@href").get()
            category_id = re.search(r'cid=(\d+)', category_href).group(1)
            print(category_name, category_href, category_id)
            yield {
                'type': "category",
                'source': "baidu",
                'id': category_id,
                'name': category_name,
                'index': [category_id],
            }

            # 二级分类
            child_category_list = category.xpath("./div/a")
            for child_category in child_category_list:
                child_category_name = child_category.xpath("./text()").get()
                child_category_href = child_category.xpath("./@href").get()
                child_category_id = re.search(r'cid=(\d+)', child_category_href).group(1)
                yield {
                    'type': "category",
                    'source': "baidu",
                    'id': child_category_id,
                    'name': child_category_name,
                    'index': [category_id, child_category_id],
                }
                # 请求二级分类的分页页面
                yield scrapy.Request(
                    url='https://shurufa.baidu.com' + child_category_href,
                    callback=self.parse_pages,
                    cb_kwargs={"parent_index": [category_id, child_category_id]}
                )

    def parse_pages(self, response, parent_index):
        """
        解析分页信息，获取最大页码。

        功能：
        1. 从页面中提取 maxpage 属性，确定该分类下的总页数。
        2. 遍历每一页，发送请求到 parse_dict_detail 解析词条信息。

        参数：
        - response: scrapy 的 Response 对象，包含当前分类页面 HTML
        - parent_index: list，父分类ID列表，用于追溯分类层级

        返回：
        - yield scrapy.Request 对象
        """
        max_page = 1
        try:
            max_page = int(response.xpath("//*[@id='target']/@maxpage").get())
        except:
            pass

        for page in range(1, max_page + 1):
            yield scrapy.Request(
                url=f'https://shurufa.baidu.com/dict_list?cid={parent_index[-1]}&page={page}',
                callback=self.parse_dict_detail,
                cb_kwargs={"parent_index": parent_index}
            )

    def parse_dict_detail(self, response, parent_index):
        """
        解析具体词条信息。

        功能：
        1. 遍历词条表格的每一行。
        2. 提取词条ID、名称、下载次数、更新时间、innerid以及示例内容。
        3. 拼接下载链接。
        4. yield 词条信息字典。

        参数：
        - response: scrapy 的 Response 对象，包含词条列表页面 HTML
        - parent_index: list，父分类ID列表，用于追溯层级

        返回：
        - yield 词条信息字典
        """
        for tr in response.xpath("//table/tr"):
            dict_id = tr.xpath("./td[1]/a/@dict-id").get()
            dict_name = tr.xpath("./td[1]/a/text()").get()
            count = tr.xpath(".//*[@class='dict-downcount']/text()").get()
            time = tr.xpath(".//*[@class='dict-time']/text()").get()
            dict_innerid = tr.xpath(".//*[@dict-innerid]/@dict-innerid").get()
            # 示例内容，用顿号连接，去掉换行
            example = '、'.join([item.replace('\n', '') for item in tr.xpath("./td[2]/span/span/text()").getall()])
            yield {
                'type': "dict",
                'source': "baidu",
                'id': dict_id,
                'name': dict_name,
                'href': 'https://shurufa.baidu.com/dict_innerid_download?innerid=' + dict_innerid,
                'example': example,
                'count': count,
                'time': time,
                'index': parent_index,
            }
