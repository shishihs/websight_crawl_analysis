#!/usr/bin/env python3
"""
lifenet_sitemap.jsonに含まれるURLのステータスを確認し、
リンク切れ（ステータスコードが200以外、または接続エラー）のURLを一覧化するスクリプト
"""
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import time

def check_url(url, timeout=10):
    """URLのステータスを確認する"""
    try:
        headers = {
            'User-Agent': 'SitemapBrokenLinkChecker/1.0'
        }
        # HEADリクエストで確認（サーバーによってはHEADを拒否する場合があるので、その場合はGETで再試行）
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        if response.status_code == 405: # Method Not Allowed
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.close() # コンテンツは不要なので閉じる
            
        return url, response.status_code, None
    except requests.exceptions.RequestException as e:
        return url, None, str(e)

def main():
    json_file = "lifenet_sitemap.json"
    
    print(f"📂 {json_file} を読み込んでいます...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ エラー: {json_file} が見つかりません。")
        sys.exit(1)
        
    urls = [item['url'] for item in data.get('urls', [])]
    total_urls = len(urls)
    print(f"🔍 {total_urls} 件のURLをチェックします...")
    
    broken_links = []
    checked_count = 0
    
    # 並列処理でチェック（サーバー負荷を考慮してワーカー数は控えめに）
    max_workers = 10
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            checked_count += 1
            
            try:
                _, status_code, error = future.result()
                
                # 進捗表示
                print(f"\r[{checked_count}/{total_urls}] Checking...", end="", flush=True)
                
                if error:
                    print(f"\n❌ エラー: {url} - {error}")
                    broken_links.append({'url': url, 'status': 'Error', 'details': error})
                elif status_code >= 400:
                    print(f"\n⚠️  リンク切れ ({status_code}): {url}")
                    broken_links.append({'url': url, 'status': status_code, 'details': 'HTTP Error'})
                
            except Exception as e:
                print(f"\n❌ 予期せぬエラー: {url} - {e}")
                broken_links.append({'url': url, 'status': 'Exception', 'details': str(e)})
                
            # 少し待機（レートリミット回避）
            time.sleep(0.1)
            
    print("\n" + "=" * 60)
    print("📊 チェック結果")
    print("=" * 60)
    
    if broken_links:
        print(f"❌ {len(broken_links)} 件のリンク切れが見つかりました:\n")
        for link in broken_links:
            print(f"- {link['url']}")
            print(f"  Status: {link['status']}, Details: {link['details']}")
            print()
    else:
        print("✅ リンク切れは見つかりませんでした。")

if __name__ == "__main__":
    main()
