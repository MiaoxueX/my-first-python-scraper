# My First Python Scraper

一个适合 Python 初学者学习的、可配置的网页爬虫项目。它目前支持抓取公开练习网站 [Books to Scrape](https://books.toscrape.com/) 的图书标题和价格，并导出为 CSV 或 JSON。

> Books to Scrape 是专门用于练习爬虫的网站。抓取真实网站前，请先了解其服务条款、`robots.txt` 和访问频率限制。

## 功能

- 通过 `config.json` 选择抓取目标、字段、数量、输出路径和格式。
- 当前支持 `books` 目标，自动跟随分页，直到达到指定数量或网站没有更多图书。
- 当前 books 可选字段：`title`、`price`。
- 导出 CSV 或 JSON；输出目录不存在时会自动创建。
- 网络请求失败时自动重试两次，并提供易懂的错误提示。

## 安装

建议先创建并启用虚拟环境，再安装依赖：

```bash
python -m pip install -r requirements.txt
```

## 配置

修改项目根目录的 `config.json`：

```json
{
  "target": "books",
  "fields": ["title", "price"],
  "count": 20,
  "output": "data/books.csv",
  "format": "csv"
}
```

每一项的含义如下：

| 配置项 | 说明 |
| --- | --- |
| `target` | 要抓取的目标。目前仅支持 `books`。 |
| `fields` | 要保存的字段列表。books 支持 `title` 和 `price`。省略时默认使用 `title`、`price`。 |
| `count` | 要抓取的最大数量，必须是正整数。 |
| `output` | 输出文件路径，例如 `data/books.csv` 或 `output/books.json`。目录会自动创建。 |
| `format` | 导出格式，只能是 `csv` 或 `json`。 |

### fields 示例

只保存标题：

```json
{
  "target": "books",
  "fields": ["title"],
  "count": 5,
  "output": "data/book_titles.json",
  "format": "json"
}
```

如果写入不支持的字段，例如 `"rating"`，程序会提示 books 支持哪些字段；不会静默生成错误数据。

## 运行

```bash
python main.py
```

旧的入口文件仍可使用：

```bash
python scrape_books.py
```

一次成功运行的输出类似：

```text
Scraping started...
Target: books
Fields: title, price
Count: 20
Format: csv
Output: data/books.csv

Scraping...
20 item(s) collected.

Export completed:
data/books.csv
```

如果网站可用的数据少于 `count`，程序会导出已收集的数据，并清楚提示实际数量。

## 项目结构

```text
.
├── config.json              # 用户修改的抓取配置
├── main.py                  # 推荐的程序入口
├── scrape_books.py          # 兼容旧运行命令的入口
├── core/
│   ├── config.py            # 读取和验证配置
│   └── manager.py           # 组合 crawler 与 exporter
├── crawlers/
│   ├── base.py              # 请求、重试和统一抓取接口
│   └── books.py             # Books to Scrape 的分页和解析逻辑
├── exporters/
│   ├── base.py              # 统一导出接口
│   ├── csv_exporter.py      # CSV 导出
│   └── json_exporter.py     # JSON 导出
├── tests/                   # 不依赖外网的自动化测试
└── data/                    # 默认输出目录
```

## 为什么使用类？

类让每一部分只做一件清楚的事：

- `ScraperConfig` 负责读取、检查 `config.json`。
- `BaseCrawler` 负责通用的请求、超时和重试；`BookCrawler` 只负责图书网站的页面和数据解析。
- `BaseExporter` 定义统一的保存方式；`CsvExporter` 和 `JsonExporter` 分别实现两种格式。
- `ScraperManager` 根据配置选择正确的 crawler 和 exporter，并安排完整流程。

因此，抓取网站的代码不需要知道文件如何保存，导出器也不需要知道网页如何解析。`fields` 从配置传给 crawler，crawler 只返回所选字段，两个 exporter 因而都会只写入用户指定的字段。

## 未来增加 MovieCrawler

当需要支持电影网站时：

1. 新建 `crawlers/movies.py`，让 `MovieCrawler` 继承 `BaseCrawler` 并实现 `collect()`；
2. 在 `core/config.py` 中为 `movies` 声明默认字段和可用字段；
3. 在 `core/manager.py` 的 `crawler_types` 中注册 `"movies": MovieCrawler`；
4. 在 `config.json` 设置 `"target": "movies"`。

CSV 与 JSON 导出器不需要修改，因为它们都接收统一的字典列表。

## 测试

运行离线自动化测试：

```bash
python -m unittest discover -s tests -v
```
