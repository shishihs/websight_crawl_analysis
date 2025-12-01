# Architecture Overview

## System Overview
The **WebSight Analysis** tool is a Python-based web crawler and visualization suite designed to analyze website structures, identify broken links, and visualize page relationships using interactive graphs.

## Core Components

### 1. Web Crawler (`web_crawler.py`)
- **Purpose**: Discovers pages by crawling from a start URL.
- **Algorithm**: Breadth-First Search (BFS).
- **Features**:
  - Parallel processing (ThreadPoolExecutor).
  - Domain restriction (stays within the target domain).
  - Full link tracking (records all `<a>` tags for In-Degree calculation).
  - Respects `robots.txt` (implicitly via user-agent) and server load (sleep delays).

### 2. Data Model (`sitemap_data.py`)
- **`SitemapURL`**: Represents a single URL.
  - `url`: Full URL.
  - `status_code`: HTTP status code.
  - `referrers`: List of URLs linking to this page.
  - `in_degree`: Count of incoming links (centrality metric).
  - `discovery_parent`: The URL from which this page was first discovered.
- **`SitemapData`**: Container for `SitemapURL` objects.
  - `url_map`: Dictionary for O(1) URL lookups.
  - `add_referrer()`: Updates link relationships.

### 3. Visualizer (`sitemap_visualizer.py`)
- **Purpose**: Generates the interactive HTML report.
- **Technologies**: Python (generation), HTML/CSS, JavaScript (ECharts).
- **Key Features**:
  - **Force Directed Graph**: Visualizes site structure.
    - **Dynamic Sizing**: Node size based on In-Degree.
    - **Clustering**: Nodes grouped by directory/category.
    - **Filtering**: Excludes global navigation (top 5% linked) and non-HTML files.
  - **Global Navigation Analysis**: Identifies common header/footer links.
  - **Isolated Page Detection**: Lists pages with few incoming links.

### 4. Entry Point (`crawl_lifenet.py`)
- **Purpose**: CLI interface to orchestrate the crawling and reporting process.
- **Arguments**: `--url`, `--max-pages`, `--workers`.

## Data Flow
1.  **Input**: User provides a Start URL.
2.  **Crawl**: `WebCrawler` fetches pages, extracts links, and builds the `SitemapData` graph.
3.  **Process**: In-Degree centrality is calculated during the crawl.
4.  **Visualize**: `SitemapVisualizer` processes the data:
    - Aggregates nodes (merges query params).
    - Filters noise (images, PDFs, global nav).
    - Generates JSON for ECharts.
5.  **Output**: `lifenet_crawl_report.html` (and JSON/CSV data).
