# 词库爬虫 (Dict Spider)

一个基于 Scrapy 框架的分布式爬虫项目，用于爬取搜狗输入法和百度输入法的词库数据。项目采用模块化设计，支持分类层级解析、分页处理和数据持久化存储。

## 项目特性

- 🚀 **多平台支持**: 支持搜狗输入法和百度输入法词库爬取
- 📊 **层级分类**: 自动解析多级分类结构（一级、二级、三级分类）
- 🔄 **分页处理**: 智能识别并处理分页数据
- 💾 **数据持久化**: 支持 MongoDB 数据库存储
- 🌐 **代理支持**: 内置 HTTP 代理中间件，支持代理池
- ⚡ **高性能**: 支持并发请求和自动限流
- 🛡️ **异常处理**: 完善的异常处理机制，保证爬虫稳定运行

## 项目结构

```
dict_spider_new/
├── dict_spider/                 # Scrapy 项目主目录
│   ├── __init__.py
│   ├── items.py                 # 数据模型定义
│   ├── middlewares.py           # 中间件配置
│   ├── pipelines.py             # 数据管道（MongoDB 存储）
│   ├── settings.py              # 项目配置
│   └── spiders/                 # 爬虫模块
│       ├── __init__.py
│       ├── baidu.py             # 百度输入法爬虫
│       ├── sogou.py             # 搜狗输入法爬虫
│       └── ip.py                # IP 检测爬虫
├── debug_spider.py              # 调试脚本
├── requirements.txt             # 依赖包列表
├── scrapy.cfg                   # Scrapy 配置文件
├── LICENSE                      # GPL v3.0 许可证
└── README.md                    # 项目说明文档
```

## 环境依赖

- Python 3.10+
- Scrapy 2.13.3
- PyMongo 4.15.3
- ItemAdapter 0.12.2

### 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 配置 MongoDB 数据库

确保本地 MongoDB 服务正在运行（默认端口 27017）：

```bash
# 启动 MongoDB 服务
mongod
```

### 2. 配置代理（可选）

如果需要使用代理，设置环境变量：

```bash
export http_proxy="http://username:password@host:port"
export https_proxy="http://username:password@host:port"
```

### 3. 运行爬虫

#### 运行搜狗输入法爬虫

```bash
scrapy crawl sogou
```

#### 运行百度输入法爬虫

```bash
scrapy crawl baidu
```

#### 使用调试脚本

```bash
python debug_spider.py
```

## 数据模型

### 分类数据 (Category)

| 字段名    | 类型     | 含义           |
|--------|--------|--------------|
| type   | string | 数据类型（固定为 "category"） |
| source | string | 数据源（"sogou" 或 "baidu"） |
| id     | string | 分类唯一标识符      |
| name   | string | 分类名称         |
| index  | list   | 分类层级路径       |

### 词条数据 (Dictionary)

| 字段名    | 类型     | 含义           |
|--------|--------|--------------|
| type   | string | 数据类型（固定为 "dict"） |
| source | string | 数据源（"sogou" 或 "baidu"） |
| id     | string | 词条唯一标识符      |
| name   | string | 词条名称         |
| href   | string | 下载链接         |
| example| string | 示例内容         |
| count  | string | 下载次数         |
| time   | string | 更新时间         |
| index  | list   | 所属分类层级路径    |

## 爬虫功能详解

### 搜狗输入法爬虫 (SogouSpider)

- **起始 URL**: `https://pinyin.sogou.com/dict/`
- **功能特点**:
  - 解析三级分类结构
  - 支持城市列表分类
  - 自动分页处理
  - 提取词条详细信息

### 百度输入法爬虫 (BaiduSpider)

- **起始 URL**: `https://shurufa.baidu.com/dict.html`
- **功能特点**:
  - 解析二级分类结构
  - 智能分页识别
  - 提取 innerid 用于下载
  - 支持示例内容提取

## 配置说明

### 主要配置项

- `CONCURRENT_REQUESTS = 32`: 并发请求数
- `DOWNLOAD_DELAY = 0`: 下载延迟
- `RETRY_TIMES = 10`: 重试次数
- `AUTOTHROTTLE_ENABLED = True`: 启用自动限流
- `ROBOTSTXT_OBEY = False`: 不遵守 robots.txt

### 数据库配置

- **数据库**: `dict_spider`
- **集合**: `sogou`、`baidu`
- **索引**: 基于 `type` 和 `id` 的复合唯一索引

## 下载链接格式

### 搜狗输入法
```
https://pinyin.sogou.com/d/dict/download_cell.php?id={dict_id}&name={dict_name}
```

### 百度输入法
```
https://shurufa.baidu.com/dict_innerid_download?innerid={dict_innerid}
```

## 开发说明

### 添加新的爬虫

1. 在 `spiders/` 目录下创建新的爬虫文件
2. 继承 `scrapy.Spider` 类
3. 实现必要的解析方法
4. 在 `settings.py` 中配置相应的中间件和管道

### 自定义数据处理

修改 `pipelines.py` 中的 `DictSpiderPipeline` 类来自定义数据处理逻辑。

## 注意事项

1. **遵守网站规则**: 请合理控制爬取频率，避免对目标网站造成过大压力
2. **数据使用**: 爬取的数据仅供学习和研究使用
3. **法律风险**: 使用者需自行承担使用本项目带来的法律风险
4. **代理使用**: 建议使用代理池以提高爬取成功率

## 故障排除

### 常见问题

1. **MongoDB 连接失败**: 确保 MongoDB 服务正在运行
2. **代理连接失败**: 检查代理配置是否正确
3. **爬取失败**: 检查网络连接和目标网站状态

### 日志查看

项目启用了详细的日志记录，可以通过日志信息排查问题：

```bash
scrapy crawl sogou -L INFO
```

## 法律声明

本项目仅用于技术学习与研究目的，禁止用于任何违反地区及目标网站法律法规的用途。使用者需自行承担使用本项目带来的全部法律风险。若目标网站对抓取行为有异议，请联系删除相关代码或数据。

## 许可证

本项目基于 [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) 开源发布。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进本项目。

## 更新日志

- **v1.0.0**: 初始版本，支持搜狗和百度输入法词库爬取
- 支持多级分类解析
- 支持 MongoDB 数据存储
- 支持代理配置

