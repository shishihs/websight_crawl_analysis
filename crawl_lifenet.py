"""
ライフネット生命ウェブサイトクローラー実行スクリプト
"""
import argparse
from web_crawler import WebCrawler
from sitemap_visualizer import SitemapVisualizer
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='ウェブサイト構造解析クローラー')
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
    data.save_json("lifenet_crawl_data.json")
    data.save_csv("lifenet_crawl_data.csv")
    
    # レポート生成
    print("\n🎨 レポートを生成中...")
    visualizer = SitemapVisualizer(data)
    visualizer.generate_html_report("lifenet_crawl_report.html", title="ライフネット生命 サイト構造解析レポート")
    
    print("\n✅ 完了しました！")
    print("   open lifenet_crawl_report.html")

if __name__ == "__main__":
    main()
