# WebSight Analysis

**WebSight Analysis** is a comprehensive tool for crawling, analyzing, and visualizing website structures. It goes beyond simple sitemap parsing to discover the actual link graph of a website, identifying key hubs, isolated pages, and structural patterns.

## Key Features
- **🕷️ Smart Crawler**: BFS-based crawler with parallel processing and full link tracking.
- **🧠 Interactive Mind Map**: Force-directed graph visualization using ECharts.
  - **Dynamic Sizing**: Node sizes reflect page importance (In-Degree Centrality).
  - **Noise Filtering**: Automatically excludes global navigation and non-HTML assets.
- **📊 Advanced Analysis**:
  - **Global Navigation Detection**: Identifies common header/footer links.
  - **Isolated Page Detection**: Finds deep or orphaned content.
  - **Broken Link Checker**: Reports 404s and other errors.

## Quick Start

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Choose Analysis Method**:

    **Option A: Full Analysis (Sitemap + Crawl)**
    ```bash
    python3 analyze_all.py --sitemap-url https://example.com/sitemap.xml --crawl-url https://example.com/
    ```

    **Option B: Crawl Only**
    ```bash
    python3 crawl_websight.py --url https://example.com/
    ```

    **Option C: Sitemap Only**
    ```bash
    python3 analyze_websight.py
    ```

3.  **View Reports**:
    - `websight_crawl_report.html` - Crawl analysis
    - `websight_sitemap_report.html` - Sitemap analysis

## Documentation
- [Architecture Overview](docs/architecture.md): System design and component details.
- [Usage Guide](docs/usage.md): Detailed command-line options and report explanation.

## Project Structure
- `crawl_websight.py`: Main entry point for web crawling.
- `analyze_websight.py`: Entry point for sitemap.xml analysis.
- `web_crawler.py`: Crawling logic.
- `sitemap_visualizer.py`: Report generation and visualization logic.
- `sitemap_data.py`: Data models.
