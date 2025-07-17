# 词库爬虫

用于爬取搜狗、百度、QQ 三大输入法的词库数据。

## 环境依赖

- Python 3.13.5
- Scrapy 2.13.3

安装依赖：

```bash
pip install -r requirements.txt
````

## 使用方式

配置代理池:
创建 [dict_spider/.env](dict_spider/.env) 文件并设置代理池接口地址，用于轮询获取可用代理IP

```
PROXY_POOL_URL=https://your-proxy-pool-address/api/get
```

运行爬虫：

```bash
scrapy crawl sogou
scrapy crawl baidu
scrapy crawl qq
```

## 输出格式

结果将保存为 `.csv` 文件，包含以下字段：

| 字段名              | 含义        |
|------------------|-----------|
| `dict_id`        | 词条唯一 ID   |
| `dict_pid`       | 父级词条 ID   |
| `dict_name`      | 词条名称      |
| `dict_innerid`   | 内部唯一标识符   |
| `dict_time`      | 发布时间或更新时间 |
| `dict_downcount` | 下载次数或热度指标 |
| `dict_exps`      | 词条内容示例    |
| `dict_tiers`     | 词条层级      |

## 下载地址

- Baidu: https://shurufa.baidu.com/dict_innerid_download?innerid={dict_innerid}
- Sougo: https://pinyin.sogou.com/d/dict/download_cell.php?id={dict_id}&name={dict_name}
- QQ: https://cdict.qq.pinyin.cn/v1/download?dict_id={dict_id}

## 法律声明

本项目仅用于技术学习与研究目的，禁止用于任何违反地区及目标网站法律法规的用途。使用者需自行承担使用本项目带来的全部法律风险。若目标网站对抓取行为有异议，请联系删除相关代码或数据。

## 许可证

本项目基于 [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) 开源发布。

