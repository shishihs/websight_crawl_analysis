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

2.  **Run the Crawler**:
    ```bash
    python3 crawl_websight.py --url https://www.lifenet-seimei.co.jp/
    ```

3.  **View Report**:
    Open `websight_crawl_report.html` in your browser.

## Documentation
- [Architecture Overview](docs/architecture.md): System design and component details.
- [Usage Guide](docs/usage.md): Detailed command-line options and report explanation.

## Project Structure
- `crawl_websight.py`: Main entry point for web crawling.
- `analyze_websight.py`: Entry point for sitemap.xml analysis.
- `web_crawler.py`: Crawling logic.
- `sitemap_visualizer.py`: Report generation and visualization logic.
- `sitemap_data.py`: Data models.
