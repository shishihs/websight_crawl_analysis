# Usage Guide

## Installation
1.  **Prerequisites**: Python 3.8+
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Crawler
The main entry point is `crawl_websight.py`.

### Basic Usage
Crawl a website with default settings:
```bash
python3 crawl_websight.py --url https://example.com/
```

### Custom URL
Crawl a specific website:
```bash
python3 crawl_websight.py --url https://example.com/
```

### Configuration Options
| Argument | Default | Description |
|----------|---------|-------------|
| `--url` | `https://www.lifenet-seimei.co.jp/` | The starting URL for the crawl. |
| `--max-pages` | `500` | Maximum number of pages to crawl. Increase for larger sites. |
| `--workers` | `10` | Number of parallel worker threads. Decrease to reduce server load. |

**Example: Large Crawl with Low Load**
```bash
python3 crawl_websight.py --url https://example.com/ --max-pages 2000 --workers 2
```

## Understanding the Report
The generated `websight_crawl_report.html` contains:

1.  **Site Structure Mind Map**:
    - Interactive graph showing page relationships.
    - **Node Size**: Larger nodes have more incoming links (higher importance).
    - **Colors**: Grouped by directory/category.
    - **Tooltips**: Hover to see "Category > Page Name".
2.  **Global Navigation Analysis**:
    - Lists links that appear on >5% of all pages (likely headers/footers).
    - These are excluded from the graph to prevent clutter.
3.  **Isolated Pages**:
    - Lists index pages with <= 2 incoming links.
    - Useful for finding "orphan" or hard-to-reach content.
4.  **URL List**:
    - Searchable table of all discovered URLs with status codes and referrers.
