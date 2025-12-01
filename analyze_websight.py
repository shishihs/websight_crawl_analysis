#!/usr/bin/env python3
"""
ライフネット生命保険のサイトマップ解析スクリプト
使用方法: python analyze_lifenet.py
"""
import sys
from sitemap_analyzer import SitemapAnalyzer
from sitemap_visualizer import SitemapVisualizer


def main():
    print("=" * 60)
    print("🔍 ライフネット生命保険 サイトマップ解析ツール")
    print("=" * 60)
    print()
    
    # ライフネット生命のドメイン
    domain = "https://www.lifenet-seimei.co.jp"
    
    # 解析器を初期化
    # リンクチェックを有効化（解析時間が長くなる可能性があります）
    analyzer = SitemapAnalyzer(check_links=True)
    
    # サイトマップURLを自動検出
    sitemap_url = analyzer.discover_sitemap(domain)
    
    if not sitemap_url:
        print(f"❌ エラー: {domain} のサイトマップを検出できませんでした")
        print("手動でサイトマップURLを指定してください:")
        print("例: python analyze_lifenet.py https://www.lifenet-seimei.co.jp/sitemap.xml")
        sys.exit(1)
    
    # サイトマップを解析
    print()
    print("📋 サイトマップ解析を開始します...")
    print()
    
    data = analyzer.analyze(sitemap_url)
    
    # 統計情報を表示
    print()
    print("=" * 60)
    print("📊 解析結果サマリー")
    print("=" * 60)
    
    stats = data.get_statistics()
    print(f"総URL数: {stats['total_urls']:,}")
    print(f"カテゴリ数: {len(stats['categories'])}")
    print()
    
    print("カテゴリ別URL数（上位10）:")
    sorted_categories = sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(sorted_categories[:10], 1):
        print(f"  {i:2d}. {category:30s} : {count:4d} URLs")
    
    if len(sorted_categories) > 10:
        print(f"  ... 他 {len(sorted_categories) - 10} カテゴリ")
    
    print()
    
    # データの保存
    print("\n💾 データを保存中...")
    data.save_json("websight_sitemap.json")
    data.save_csv("websight_sitemap.csv")
    
    # レポート生成
    print("\n🎨 レポートを生成中...")
    visualizer = SitemapVisualizer(data)
    visualizer.generate_html_report("websight_sitemap_report.html", title="WebSight Analysis Report")
    
    print("\n✅ 完了しました！")
    print("   open websight_sitemap_report.html")
    print()
    print("生成されたファイル:")
    print("  📄 websight_sitemap.json         - JSON形式のデータ")
    print("  📄 websight_sitemap.csv          - CSV形式のデータ")
    print("  📄 websight_sitemap_report.html  - インタラクティブなレポート")
    print()
    print("レポートを表示するには:")
    print("  open lifenet_sitemap_report.html")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  ユーザーによって中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
