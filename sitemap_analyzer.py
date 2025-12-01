"""
サイトマップ解析のコアモジュール
XMLサイトマップの取得、パース、再帰的な処理を行う
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Optional, Set
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time
import concurrent.futures
from bs4 import BeautifulSoup

from sitemap_data import SitemapData


class SitemapAnalyzer:
    """サイトマップ解析クラス"""
    
    # XMLネームスペース
    NS = {
        'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'xhtml': 'http://www.w3.org/1999/xhtml',
        'image': 'http://www.google.com/schemas/sitemap-image/1.1',
        'video': 'http://www.google.com/schemas/sitemap-video/1.1'
    }
    
    def __init__(self, user_agent: str = 'SitemapAnalyzer/1.0', check_links: bool = False):
        self.user_agent = user_agent
        self.check_links = check_links
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.processed_sitemaps: Set[str] = set()
    
    def fetch_sitemap(self, url: str, timeout: int = 30) -> Optional[str]:
        """サイトマップをHTTPで取得"""
        try:
            print(f"📡 サイトマップを取得中: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Content-Typeを確認
            content_type = response.headers.get('Content-Type', '')
            if 'xml' not in content_type and 'text' not in content_type:
                print(f"⚠️  警告: 予期しないContent-Type: {content_type}")
            
            return response.text
        
        except requests.exceptions.RequestException as e:
            print(f"❌ エラー: サイトマップの取得に失敗しました: {e}")
            return None
    
    def check_url_status(self, url: str, timeout: int = 10) -> Optional[int]:
        """URLのステータスコードを確認"""
        if not self.check_links:
            return None
            
        try:
            # HEADリクエストで確認
            response = self.session.head(url, timeout=timeout, allow_redirects=True)
            
            # 405 Method Not Allowedの場合はGETで再試行
            if response.status_code == 405:
                response = self.session.get(url, timeout=timeout, stream=True)
                response.close()
                
            # サーバー負荷軽減のため少し待機
            time.sleep(0.1)
            
            if response.status_code >= 400:
                print(f"⚠️  リンク切れ ({response.status_code}): {url}")
            
            return response.status_code
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 接続エラー: {url} - {e}")
            return None
    
    def parse_sitemap_index(self, xml_content: str) -> List[str]:
        """サイトマップインデックスをパースして、含まれるサイトマップURLのリストを返す"""
        try:
            root = ET.fromstring(xml_content)
            
            # sitemapindex要素を確認
            if root.tag.endswith('sitemapindex'):
                sitemap_urls = []
                for sitemap in root.findall('sm:sitemap', self.NS):
                    loc = sitemap.find('sm:loc', self.NS)
                    if loc is not None and loc.text:
                        sitemap_urls.append(loc.text.strip())
                
                if sitemap_urls:
                    print(f"📑 サイトマップインデックスを検出: {len(sitemap_urls)} 個のサイトマップ")
                    return sitemap_urls
            
            return []
        
        except ET.ParseError as e:
            print(f"❌ XMLパースエラー: {e}")
            return []
    
    def parse_urlset(self, xml_content: str, data: SitemapData, sitemap_url: str):
        """URLセットをパースしてSitemapDataに追加"""
        try:
            root = ET.fromstring(xml_content)
            
            # urlset要素を確認
            if not root.tag.endswith('urlset'):
                return
            
            url_count = 0
            for url_elem in root.findall('sm:url', self.NS):
                loc = url_elem.find('sm:loc', self.NS)
                if loc is None or not loc.text:
                    continue
                
                url = loc.text.strip()
                
                # オプショナルなメタデータを取得
                lastmod_elem = url_elem.find('sm:lastmod', self.NS)
                lastmod = lastmod_elem.text.strip() if lastmod_elem is not None and lastmod_elem.text else None
                
                changefreq_elem = url_elem.find('sm:changefreq', self.NS)
                changefreq = changefreq_elem.text.strip() if changefreq_elem is not None and changefreq_elem.text else None
                
                priority_elem = url_elem.find('sm:priority', self.NS)
                priority = None
                if priority_elem is not None and priority_elem.text:
                    try:
                        priority = float(priority_elem.text.strip())
                    except ValueError:
                        pass
                
                # リンクチェックは後でまとめて並列実行するため、ここではスキップ
                # status_code = self.check_url_status(url)
                
                data.add_url(url, lastmod, changefreq, priority, source_sitemap=sitemap_url)
                url_count += 1
            
            print(f"✓ {url_count} 個のURLを抽出しました")
        
        except ET.ParseError as e:
            print(f"❌ XMLパースエラー: {e}")
    
    def analyze(self, sitemap_url: str, max_depth: int = 10) -> SitemapData:
        """
        サイトマップを解析してSitemapDataを返す
        サイトマップインデックスの場合は再帰的に処理
        """
        data = SitemapData()
        data.source_url = sitemap_url
        data.fetched_at = datetime.now().isoformat()
        
        self.processed_sitemaps.clear()
        self._analyze_recursive(sitemap_url, data, depth=0, max_depth=max_depth)
        
        # リンクチェック（有効な場合）
        if self.check_links:
            self._check_links_parallel(data)
            # 参照元調査
            self.find_referrers(data)
        
        return data
    
    def _check_links_parallel(self, data: SitemapData, max_workers: int = 10):
        """並列でリンク切れをチェック"""
        urls = data.urls
        total = len(urls)
        print(f"🔍 {total} 件のURLを並列チェック中 (max_workers={max_workers})...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # URLオブジェクトとFutureのマッピング
            future_to_url = {executor.submit(self.check_url_status, url_obj.url): url_obj for url_obj in urls}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_url):
                url_obj = future_to_url[future]
                try:
                    status_code = future.result()
                    url_obj.status_code = status_code
                except Exception as e:
                    print(f"❌ エラー: {url_obj.url} - {e}")
                
                completed += 1
                if completed % 10 == 0 or completed == total:
                    print(f"\r[{completed}/{total}] Checking...", end="", flush=True)
            
            print() # 改行

    def find_referrers(self, data: SitemapData, max_workers: int = 10):
        """リンク切れURLの参照元ページを特定する"""
        # リンク切れURLを特定
        broken_urls = {u.url: u for u in data.urls if u.status_code and u.status_code >= 400}
        if not broken_urls:
            return

        # 調査対象の有効なページ（HTMLのみ）
        valid_pages = [
            u for u in data.urls 
            if u.status_code and u.status_code == 200 
            and (u.url.endswith('.html') or u.url.endswith('/'))
        ]
        
        total = len(valid_pages)
        print(f"🕵️ {total} 件の有効なページから参照元を調査中...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self._scan_page_for_links, page.url, broken_urls.keys()): page for page in valid_pages}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_url):
                page = future_to_url[future]
                try:
                    found_links = future.result()
                    for broken_link in found_links:
                        if broken_link in broken_urls:
                            broken_urls[broken_link].referrers.append(page.url)
                except Exception as e:
                    print(f"❌ 参照元調査エラー: {page.url} - {e}")
                
                completed += 1
                if completed % 10 == 0 or completed == total:
                    print(f"\r[{completed}/{total}] Scanning...", end="", flush=True)
        print()

    def _scan_page_for_links(self, page_url: str, target_urls: Set[str]) -> Set[str]:
        """ページ内のリンクを解析し、ターゲットURLが含まれているか確認"""
        found_targets = set()
        try:
            response = self.session.get(page_url, timeout=10)
            if response.status_code != 200:
                return found_targets
                
            soup = BeautifulSoup(response.content, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                absolute_url = urljoin(page_url, href)
                
                # フラグメント(#)を除去
                absolute_url = absolute_url.split('#')[0]
                
                if absolute_url in target_urls:
                    found_targets.add(absolute_url)
                    
        except Exception:
            pass
            
        return found_targets
    
    def _analyze_recursive(self, url: str, data: SitemapData, depth: int, max_depth: int):
        """再帰的にサイトマップを解析"""
        # 深さ制限チェック
        if depth > max_depth:
            print(f"⚠️  警告: 最大深度 {max_depth} に達しました")
            return
        
        # 既に処理済みかチェック
        if url in self.processed_sitemaps:
            print(f"⏭️  スキップ: 既に処理済み {url}")
            return
        
        self.processed_sitemaps.add(url)
        
        # サイトマップを取得
        xml_content = self.fetch_sitemap(url)
        if not xml_content:
            return
        
        # 少し待機（サーバー負荷軽減）
        time.sleep(0.5)
        
        # サイトマップインデックスかチェック
        sitemap_urls = self.parse_sitemap_index(xml_content)
        
        if sitemap_urls:
            # サイトマップインデックスの場合、各サイトマップを再帰的に処理
            for sitemap_url in sitemap_urls:
                self._analyze_recursive(sitemap_url, data, depth + 1, max_depth)
        else:
            # 通常のURLセットとして処理
            self.parse_urlset(xml_content, data, url)
    
    def discover_sitemap(self, domain: str) -> Optional[str]:
        """
        一般的なサイトマップの場所を試して、サイトマップURLを自動検出
        """
        # ドメインの正規化
        if not domain.startswith('http'):
            domain = 'https://' + domain
        
        parsed = urlparse(domain)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # 試すパスのリスト
        common_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap1.xml',
            '/sitemaps/sitemap.xml',
        ]
        
        print(f"🔍 サイトマップを自動検出中: {base_url}")
        
        for path in common_paths:
            url = base_url + path
            try:
                response = self.session.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    print(f"✓ サイトマップを発見: {url}")
                    return url
            except requests.exceptions.RequestException:
                continue
        
        # robots.txtから検出を試みる
        try:
            robots_url = base_url + '/robots.txt'
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        print(f"✓ robots.txtからサイトマップを発見: {sitemap_url}")
                        return sitemap_url
        except requests.exceptions.RequestException:
            pass
        
        print("❌ サイトマップを自動検出できませんでした")
        return None
