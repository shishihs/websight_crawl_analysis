"""
サイトマップデータの構造定義とデータ管理
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime
import json
import csv
from collections import defaultdict
from urllib.parse import urlparse


@dataclass
class SitemapURL:
    """サイトマップに含まれる個別URLの情報"""
    url: str
    lastmod: Optional[str] = None
    changefreq: Optional[str] = None
    priority: Optional[float] = None
    status_code: Optional[int] = None
    source_sitemap: Optional[str] = None
    referrers: List[str] = field(default_factory=list)
    discovery_parent: Optional[str] = None
    in_degree: int = 0
    
    def get_path_parts(self) -> List[str]:
        """URLのパス部分を分割して返す"""
        parsed = urlparse(self.url)
        path = parsed.path.strip('/')
        if not path:
            return ['root']
        return path.split('/')
    
    def get_category(self) -> str:
        """URLの最初のパス部分をカテゴリとして返す"""
        parts = self.get_path_parts()
        if parts == ['root'] or len(parts) == 0:
            return 'トップページ'
        return parts[0]


class SitemapData:
    """サイトマップデータの管理クラス"""
    
    def __init__(self):
        self.urls: List[SitemapURL] = []
        self.url_map: Dict[str, SitemapURL] = {}
        self.source_url: Optional[str] = None
        self.fetched_at: Optional[str] = None
    
    def add_url(self, url: str, lastmod: Optional[str] = None,
                changefreq: Optional[str] = None, priority: Optional[float] = None,
                status_code: Optional[int] = None, source_sitemap: Optional[str] = None,
                discovery_parent: Optional[str] = None):
        """URLを追加"""
        sitemap_url = SitemapURL(
            url=url,
            lastmod=lastmod,
            changefreq=changefreq,
            priority=priority,
            status_code=status_code,
            source_sitemap=source_sitemap,
            discovery_parent=discovery_parent
        )
        self.urls.append(sitemap_url)
        self.url_map[url] = sitemap_url
        
    def add_referrer(self, target_url: str, referrer_url: str):
        """参照元を追加"""
        if target_url in self.url_map:
            url_obj = self.url_map[target_url]
            if referrer_url not in url_obj.referrers:
                url_obj.referrers.append(referrer_url)
                url_obj.in_degree = len(url_obj.referrers)
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        if not self.urls:
            return {}
        
        # カテゴリ別のURL数
        category_counts = defaultdict(int)
        for url_obj in self.urls:
            category = url_obj.get_category()
            category_counts[category] += 1
        
        # 変更頻度の分布
        changefreq_counts = defaultdict(int)
        for url_obj in self.urls:
            if url_obj.changefreq:
                changefreq_counts[url_obj.changefreq] += 1
        
        # 優先度の分布
        priority_counts = defaultdict(int)
        for url_obj in self.urls:
            if url_obj.priority is not None:
                priority_counts[str(url_obj.priority)] += 1
        
        return {
            'total_urls': len(self.urls),
            'categories': dict(category_counts),
            'changefreq_distribution': dict(changefreq_counts),
            'priority_distribution': dict(priority_counts),
            'source_url': self.source_url,
            'fetched_at': self.fetched_at
        }
    
    def save_json(self, filepath: str):
        """JSON形式で保存"""
        data = {
            'source_url': self.source_url,
            'fetched_at': self.fetched_at,
            'total_urls': len(self.urls),
            'urls': [asdict(url) for url in self.urls],
            'statistics': self.get_statistics()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSONファイルを保存しました: {filepath}")
    
    def save_csv(self, filepath: str):
        """CSV形式で保存"""
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            if not self.urls:
                return
            
            fieldnames = ['url', 'lastmod', 'changefreq', 'priority', 'category', 'status_code', 'source_sitemap', 'discovery_parent', 'in_degree']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for url_obj in self.urls:
                row = asdict(url_obj)
                row['category'] = url_obj.get_category()
                # referrersはリスト型なのでCSVから除外
                row.pop('referrers', None)
                writer.writerow(row)
        
        print(f"✓ CSVファイルを保存しました: {filepath}")
    
    def load_json(self, filepath: str):
        """JSON形式から読み込み"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.source_url = data.get('source_url')
        self.fetched_at = data.get('fetched_at')
        self.urls = [SitemapURL(**url_data) for url_data in data.get('urls', [])]
        
        print(f"✓ JSONファイルを読み込みました: {filepath} ({len(self.urls)} URLs)")
