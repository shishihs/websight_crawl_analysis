"""
ライフネット生命ウェブサイトクローラー実行スクリプト
"""
import argparse
from web_crawler import WebCrawler
from sitemap_visualizer import SitemapVisualizer
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='WebSight Analysis Crawler')
    parser.add_argument('--url', type=str, default="https://www.lifenet-seimei.co.jp/", help='開始URL')
    parser.add_argument('--max-pages', type=int, default=500, help='最大取得ページ数')
    parser.add_argument('--workers', type=int, default=10, help='並列ワーカー数')
    args = parser.parse_args()
    
    start_url = args.url
    
    print(f"🚀 クローリングを開始します: {start_url}")
    print(f"   最大ページ数: {args.max_pages}")
    print(f"   ワーカー数: {args.workers}")
    
    # クローラーの初期化と実行
    crawler = WebCrawler(
        start_url=start_url, 
        max_pages=args.max_pages, 
        max_workers=args.workers
    )
    data = crawler.crawl()
    
    data.fetched_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # データの保存
    print("\n💾 データを保存中...")
    crawler.data.save_json('websight_crawl_data.json')
    print("✓ JSONファイルを保存しました: websight_crawl_data.json")
    
    crawler.data.save_csv('websight_crawl_data.csv')
    print("✓ CSVファイルを保存しました: websight_crawl_data.csv")
    
    # レポート生成
    print("\n🎨 レポートを生成中...")
    visualizer = SitemapVisualizer(crawler.data)
    visualizer.generate_html_report('websight_crawl_report.html')
    print("✓ HTMLレポートを生成しました: websight_crawl_report.html")
    
    print("\n✅ 完了しました！")
    print(f"   open websight_crawl_report.html")

if __name__ == "__main__":
    main()
