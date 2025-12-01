"""
ウェブサイトクローラー
トップページからリンクを辿ってサイト構造を解析する
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import concurrent.futures
from typing import Set, List, Dict, Optional
from collections import deque
import threading

from sitemap_data import SitemapData

class WebCrawler:
    """ウェブサイトクローラークラス"""
    
    def __init__(self, start_url: str, max_pages: int = 1000, max_workers: int = 10, user_agent: str = 'WebCrawler/1.0'):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_pages = max_pages
        self.max_workers = max_workers
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        
        self.visited: Set[str] = set()
        self.urls_to_visit: deque = deque()
        self.data = SitemapData()
        self.data.source_url = start_url
        
        # スレッドセーフなロック
        self.lock = threading.Lock()
        
    def crawl(self) -> SitemapData:
        """クローリングを実行"""
        print(f"🕷️ クローリング開始: {self.start_url}")
        print(f"   上限ページ数: {self.max_pages}")
        
        # 初期URLを追加
        self.urls_to_visit.append((self.start_url, None)) # (url, parent)
        self.visited.add(self.start_url)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            while len(self.data.urls) < self.max_pages and (self.urls_to_visit or futures):
                # 新しいタスクを追加
                while self.urls_to_visit and len(futures) < self.max_workers * 2:
                    url, parent = self.urls_to_visit.popleft()
                    future = executor.submit(self._process_url, url, parent)
                    futures.append(future)
                
                if not futures:
                    break
                
                # 完了したタスクを処理
                done, not_done = concurrent.futures.wait(futures, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED)
                futures = list(not_done)
                
                for future in done:
                    try:
                        new_links = future.result()
                        # 新しいリンクをキューに追加
                        for link in new_links:
                            with self.lock:
                                if link not in self.visited and len(self.visited) < self.max_pages:
                                    self.visited.add(link)
                                    # 親URLは現在処理中のURL
                                    # ここでは簡易的に、リンクを発見したURLを親とする
                                    # _process_url内で処理したURLが親になるが、
                                    # 並列処理の結果として返ってくるのは子リンクのリストなので
                                    # ここで親との紐付けが少し難しい。
                                    # 設計を変更し、_process_url内でdata.add_urlするようにする。
                                    pass
                    except Exception as e:
                        print(f"❌ エラー: {e}")
                
                print(f"\r[{len(self.data.urls)}/{self.max_pages}] Crawling...", end="", flush=True)
        
        print(f"\n✅ クローリング完了: {len(self.data.urls)} ページ発見")
        return self.data

    def _process_url(self, url: str, parent: Optional[str]) -> List[str]:
        """URLを処理してリンクを抽出"""
        found_links = []
        
        try:
            time.sleep(0.1) # サーバー負荷軽減
            
            # HEADリクエストでContent-Type確認（HTML以外はスキップ）
            try:
                head_resp = self.session.head(url, timeout=5, allow_redirects=True)
                content_type = head_resp.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    # HTMLでない場合もデータには追加するが、リンク解析はしない
                    with self.lock:
                        self.data.add_url(url, status_code=head_resp.status_code, discovery_parent=parent)
                    return []
            except Exception:
                pass

            # GETリクエスト
            response = self.session.get(url, timeout=10)
            status_code = response.status_code
            
            with self.lock:
                self.data.add_url(url, status_code=status_code, discovery_parent=parent)
            
            if status_code != 200:
                return []
            
            # HTML解析
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # リンク抽出
            unique_links = set()
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                absolute_url = urljoin(url, href)
                
                # フラグメント除去
                absolute_url = absolute_url.split('#')[0]
                
                # ドメイン内のみ
                if urlparse(absolute_url).netloc == self.domain:
                    # 拡張子チェック（画像などを除外）
                    if not any(absolute_url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.ico', '.pdf']):
                        unique_links.add(absolute_url)
            
            # リンクの登録と参照元の更新
            with self.lock:
                for link in unique_links:
                    # まだデータにない場合は追加
                    if link not in self.data.url_map:
                        # ステータスコードは後でチェックされるが、一旦プレースホルダーとして追加
                        self.data.add_url(link, discovery_parent=url)
                    
                    # 参照元を追加
                    self.data.add_referrer(link, url)
                    
                    # 未訪問ならキューに追加
                    if link not in self.visited and len(self.visited) < self.max_pages:
                        self.visited.add(link)
                        self.urls_to_visit.append((link, url))
                        found_links.append(link)
            
            # 参照元情報の更新（既存のURLに対しても行う）
            # これはデータ量が多くなるので、今回は「発見時の親」を重視し、
            # 全参照元の追跡はオプション（または別のフェーズ）とするのが良いが、
            # 要件にあるので簡易的に追加しておく
            # ただし、WebCrawlerクラス内ではSitemapURLオブジェクトへのアクセスが少し面倒
            # ここではdiscovery_parentを優先する
            
        except Exception as e:
            print(f"❌ {url} - {e}")
            with self.lock:
                # エラーでも登録はしておく
                self.data.add_url(url, status_code=0, discovery_parent=parent)
        
        return found_links
