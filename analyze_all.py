#!/usr/bin/env python3
"""
WebSight 総合分析スクリプト
sitemap.xml解析とウェブクロールの両方を実行
"""

import argparse
from sitemap_analyzer import SitemapAnalyzer
from sitemap_visualizer import SitemapVisualizer
from web_crawler import WebCrawler
from sitemap_data import SitemapData

def main():
    parser = argparse.ArgumentParser(description='WebSight Total Analysis (Sitemap + Crawl)')
    parser.add_argument('--sitemap-url', type=str, required=True, help='sitemap.xmlのURL')
    parser.add_argument('--crawl-url', type=str, help='クロール開始URL (指定しない場合はsitemapのみ)')
    parser.add_argument('--max-pages', type=int, default=500, help='最大クロールページ数')
    parser.add_argument('--workers', type=int, default=10, help='並列ワーカー数')
    parser.add_argument('--skip-sitemap', action='store_true', help='sitemap解析をスキップ')
    parser.add_argument('--skip-crawl', action='store_true', help='クロールをスキップ')
    args = parser.parse_args()
    
    # === Sitemap.xml 解析 ===
    if not args.skip_sitemap:
        print("=" * 60)
        print("📄 Sitemap.xml 解析")
        print("=" * 60)
        print(f"🔍 解析開始: {args.sitemap_url}\n")
        
        analyzer = SitemapAnalyzer(check_links=True)
        sitemap_data = analyzer.analyze(args.sitemap_url)
        
        # データ保存
        print("\n💾 データを保存中...")
        sitemap_data.save_json("websight_sitemap_data.json")
        sitemap_data.save_csv("websight_sitemap_data.csv")
        
        # レポート生成
        print("\n🎨 レポートを生成中...")
        visualizer = SitemapVisualizer(sitemap_data)
        visualizer.generate_html_report("websight_sitemap_report.html", title="WebSight Sitemap Analysis")
        
        print("\n✅ Sitemap解析完了！")
        print(f"   📊 {len(sitemap_data.urls)} URLs 発見")
        print(f"   📄 websight_sitemap_report.html\n")
    
    # === ウェブクロール ===
    if not args.skip_crawl and args.crawl_url:
        print("\n" + "=" * 60)
        print("🕷️ ウェブクロール")
        print("=" * 60)
        print(f"🚀 クロール開始: {args.crawl_url}")
        print(f"   最大ページ数: {args.max_pages}")
        print(f"   ワーカー数: {args.workers}\n")
        
        crawler = WebCrawler(max_workers=args.workers)
        crawler.crawl(args.crawl_url, max_pages=args.max_pages)
        
        # データ保存
        print("\n💾 データを保存中...")
        crawler.data.save_json('websight_crawl_data.json')
        crawler.data.save_csv('websight_crawl_data.csv')
        
        # レポート生成
        print("\n🎨 レポートを生成中...")
        visualizer = SitemapVisualizer(crawler.data)
        visualizer.generate_html_report('websight_crawl_report.html')
        
        print("\n✅ クロール完了！")
        print(f"   📊 {len(crawler.data.urls)} ページ発見")
        print(f"   📄 websight_crawl_report.html\n")
    
    # === 統合サマリー ===
    print("\n" + "=" * 60)
    print("📋 生成されたレポート")
    print("=" * 60)
    if not args.skip_sitemap:
        print("📄 websight_sitemap_report.html - Sitemap.xml解析レポート")
    if not args.skip_crawl and args.crawl_url:
        print("📄 websight_crawl_report.html - ウェブクロールレポート")
    print()

if __name__ == "__main__":
    main()
