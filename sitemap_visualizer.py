"""
サイトマップの可視化モジュール
インタラクティブなHTMLレポートを生成
"""
from typing import Dict
from sitemap_data import SitemapData
import json
from datetime import datetime
from urllib.parse import urlparse


class SitemapVisualizer:
    """サイトマップ可視化クラス"""
    
    def __init__(self, data: SitemapData):
        self.data = data
    
    def generate_html_report(self, output_path: str, title: str = "サイトマップ解析レポート"):
        """インタラクティブなHTMLレポートを生成"""
        stats = self.data.get_statistics()
        
        # ツリー構造データを生成
        tree_data = self._build_tree_structure()
        
        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }}
        
        h1 {{
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .meta-info {{
            color: #718096;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        
        .section {{
            background: #f7fafc;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 1px solid #e2e8f0;
        }}
        
        .section h2 {{
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .category-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .category-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }}
        
        .category-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .category-name {{
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        
        .category-count {{
            color: #667eea;
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .url-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .url-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .url-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e2e8f0;
            color: #2d3748;
        }}
        
        .url-table tr:hover {{
            background: #f7fafc;
        }}
        
        .url-link {{
            color: #667eea;
            text-decoration: none;
            word-break: break-all;
        }}
        
        .url-link:hover {{
            text-decoration: underline;
        }}
        
        .search-box {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 1em;
            margin-bottom: 20px;
            transition: border-color 0.3s ease;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .tree-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            max-height: 800px;
            overflow-y: auto;
        }}
        
        .tree-node {{
            padding: 8px 12px;
            margin: 4px 0;
            cursor: pointer;
            border-radius: 5px;
            transition: background 0.2s ease;
        }}
        
        .tree-node:hover {{
            background: #edf2f7;
        }}
        
        .tree-node-expanded {{
            font-weight: 600;
            color: #667eea;
        }}
        
        .tree-children {{
            margin-left: 20px;
            border-left: 2px solid #e2e8f0;
            padding-left: 10px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            background: #667eea;
            color: white;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 8px;
        }}
        
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
            display: inline-block;
            min-width: 60px;
            text-align: center;
        }}
        
        .status-2xx {{ background-color: #48bb78; }}
        .status-3xx {{ background-color: #ecc94b; color: #744210; }}
        .status-4xx {{ background-color: #f56565; }}
        .status-5xx {{ background-color: #e53e3e; }}
        .status-none {{ background-color: #a0aec0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="meta-info">
            <div>取得元: <strong>{stats.get('source_url', 'N/A')}</strong></div>
            <div>取得日時: <strong>{stats.get('fetched_at', 'N/A')}</strong></div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">総URL数</div>
                <div class="stat-value">{stats.get('total_urls', 0):,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">カテゴリ数</div>
                <div class="stat-value">{len(stats.get('categories', {})):,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">解析完了</div>
                <div class="stat-value">✓</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 カテゴリ別URL数</h2>
            <div class="category-list">
                {self._generate_category_html(stats.get('categories', {}))}
            </div>
        </div>
        
        <div class="section">
            <h2>🌳 サイト構造ツリー</h2>
            <div class="tree-container" id="tree-container">
                {self._generate_tree_html(tree_data)}
            </div>
        </div>

        <div class="section">
            <h2>🧠 サイトマップマインドマップ</h2>
            <p style="margin-bottom: 10px; color: #666;">※ ノードの大きさは被リンク数（重要度）を表しています。PDFや画像は除外されています。</p>
            <div id="mindmap" style="width: 100%; height: 800px;"></div>
        </div>
        
        <div class="section">
            <h2>🧭 グローバルナビゲーション分析</h2>
            <p style="margin-bottom: 10px; color: #666;">全ページの5%以上からリンクされている共通リンク（ヘッダー/フッター等）<br>※これらはマインドマップからは除外されています。</p>
            <div class="category-list">
                {self._generate_global_nav_html()}
            </div>
        </div>

        <div class="section">
            <h2>⚠️ 孤立・潜在的問題ページ</h2>
            <p style="margin-bottom: 10px; color: #666;">被リンク数が少ない（2以下）のインデックスページ</p>
            <div style="overflow-x: auto;">
                {self._generate_isolated_pages_html()}
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 URL一覧</h2>
            <input type="text" class="search-box" id="search-box" placeholder="URLを検索...">
            <div style="overflow-x: auto;">
                <table class="url-table" id="url-table">
                    <thead>
                        <tr>
                            <th>URL</th>
                            <th>カテゴリ</th>
                            <th>ステータス</th>
                            <th>ソース</th>
                            <th>参照元</th>
                            <th>最終更新</th>
                            <th>変更頻度</th>
                            <th>優先度</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_url_table_rows()}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // 検索機能
        const searchBox = document.getElementById('search-box');
        const table = document.getElementById('url-table');
        const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
        
        searchBox.addEventListener('input', function() {{
            const searchTerm = this.value.toLowerCase();
            
            for (let row of rows) {{
                const url = row.cells[0].textContent.toLowerCase();
                const category = row.cells[1].textContent.toLowerCase();
                
                if (url.includes(searchTerm) || category.includes(searchTerm)) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }}
        }});
        
        // ツリーの折りたたみ機能
        document.querySelectorAll('.tree-node-expanded').forEach(node => {{
            node.addEventListener('click', function(e) {{
                e.stopPropagation();
                const children = this.nextElementSibling;
                if (children && children.classList.contains('tree-children')) {{
                    children.style.display = children.style.display === 'none' ? 'block' : 'none';
                    this.querySelector('.badge').textContent = 
                        children.style.display === 'none' ? '+' : '-';
                }}
            }});
        }});
        
        // マインドマップ（グラフ）の描画
        const chartDom = document.getElementById('mindmap');
        const myChart = echarts.init(chartDom);
        const graphData = {self._build_graph_data()};
        
        const option = {{
            tooltip: {{
                formatter: function (params) {{
                    if (params.dataType === 'node') {{
                        // ドメインを除去して表示
                        try {{
                            const url = new URL(params.data.value);
                            return params.data.categoryName + ' > ' + url.pathname;
                        }} catch (e) {{
                            return params.data.categoryName + ' > ' + params.name;
                        }}
                    }}
                    return params.name;
                }}
            }},
            legend: [
                {{
                    data: graphData.categories.map(function (a) {{
                        return a.name;
                    }})
                }}
            ],
            series: [
                {{
                    name: 'Site Structure',
                    type: 'graph',
                    layout: 'force',
                    data: graphData.nodes,
                    links: graphData.links,
                    categories: graphData.categories,
                    roam: true,
                    label: {{
                        show: false,
                        position: 'right',
                        formatter: '{{b}}'
                    }},
                    labelLayout: {{
                        hideOverlap: true
                    }},
                    scaleLimit: {{
                        min: 0.4,
                        max: 2
                    }},
                    lineStyle: {{
                        color: 'source',
                        curveness: 0.3
                    }},
                    force: {{
                        repulsion: 1000,
                        edgeLength: [50, 200],
                        gravity: 0.1
                    }},
                    emphasis: {{
                        focus: 'adjacency',
                        lineStyle: {{
                            width: 10
                        }}
                    }}
                }}
            ]
        }};
        
        myChart.setOption(option);
        
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTMLレポートを生成しました: {output_path}")
    
    def _generate_category_html(self, categories: Dict[str, int]) -> str:
        """カテゴリリストのHTML生成"""
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        html_parts = []
        for category, count in sorted_categories:
            html_parts.append(f"""
                <div class="category-item">
                    <div class="category-name">{category}</div>
                    <div class="category-count">{count:,}</div>
                </div>
            """)
        
        return '\n'.join(html_parts)
    
    def _get_status_badge(self, status_code: int) -> str:
        """ステータスコードに応じたバッジHTMLを生成"""
        if status_code is None:
            return '<span class="status-badge status-none">N/A</span>'
            
        css_class = 'status-none'
        if 200 <= status_code < 300:
            css_class = 'status-2xx'
        elif 300 <= status_code < 400:
            css_class = 'status-3xx'
        elif 400 <= status_code < 500:
            css_class = 'status-4xx'
        elif 500 <= status_code < 600:
            css_class = 'status-5xx'
            
        return f'<span class="status-badge {css_class}">{status_code}</span>'

    def _generate_url_table_rows(self) -> str:
        """URLテーブルの行を生成"""
        rows = []
        for url_obj in self.data.urls:
            status_badge = self._get_status_badge(url_obj.status_code)
            
            referrers_html = 'N/A'
            if url_obj.referrers:
                referrer_links = [f'<a href="{ref}" target="_blank" class="url-link">{ref}</a>' for ref in url_obj.referrers[:3]]
                more_count = len(url_obj.referrers) - 3
                if more_count > 0:
                    referrers_html = '<br>'.join(referrer_links) + f'<br>... 他{more_count}件'
                else:
                    referrers_html = '<br>'.join(referrer_links)
            
            rows.append(f"""
                <tr>
                    <td><a href="{url_obj.url}" target="_blank" class="url-link">{url_obj.url}</a></td>
                    <td>{url_obj.get_category()}</td>
                    <td>{status_badge}</td>
                    <td title="{url_obj.source_sitemap or ''}">{url_obj.source_sitemap.split('/')[-1] if url_obj.source_sitemap else 'N/A'}</td>
                    <td>{referrers_html}</td>
                    <td>{url_obj.lastmod or 'N/A'}</td>
                    <td>{url_obj.changefreq or 'N/A'}</td>
                    <td>{url_obj.priority if url_obj.priority is not None else 'N/A'}</td>
                </tr>
            """)
        
        return '\n'.join(rows)
    
    def _build_tree_structure(self) -> Dict:
        """URLからツリー構造を構築"""
        tree = {"name": "root", "children": {}}
        
        for url_obj in self.data.urls:
            parts = url_obj.get_path_parts()
            current = tree
            
            for part in parts:
                if part not in current["children"]:
                    current["children"][part] = {"name": part, "children": {}, "urls": []}
                current = current["children"][part]
            
            current["urls"].append(url_obj.url)
        
        return tree
    
    def _generate_tree_html(self, node: Dict, level: int = 0) -> str:
        """ツリー構造のHTML生成（再帰的）"""
        if not node.get("children") and not node.get("urls"):
            return ""
        
        html_parts = []
        
        # 子ノードを処理
        for child_name, child_node in sorted(node.get("children", {}).items()):
            url_count = self._count_urls(child_node)
            
            html_parts.append(f"""
                <div class="tree-node tree-node-expanded">
                    📁 {child_name} <span class="badge">-</span> <span style="color: #718096; font-size: 0.9em;">({url_count} URLs)</span>
                </div>
            """)
            
            child_html = self._generate_tree_html(child_node, level + 1)
            if child_html:
                html_parts.append(f'<div class="tree-children">{child_html}</div>')
        
        # URLを処理
        for url in node.get("urls", []):
            html_parts.append(f"""
                <div class="tree-node">
                    📄 <a href="{url}" target="_blank" class="url-link">{url.split('/')[-1] or 'index'}</a>
                </div>
            """)
        
        return '\n'.join(html_parts)
    
    def _count_urls(self, node: Dict) -> int:
        """ノード内の総URL数をカウント"""
        count = len(node.get("urls", []))
        for child in node.get("children", {}).values():
            count += self._count_urls(child)
        return count

    def _build_graph_data(self) -> str:
        """グラフ可視化用のJSONデータを生成"""
        nodes = []
        links = []
        categories = []
        category_map = {}
        
        # カテゴリの抽出
        unique_categories = sorted(list(set(u.get_category() for u in self.data.urls)))
        for i, cat in enumerate(unique_categories):
            categories.append({"name": cat})
            category_map[cat] = i
            
        # URLの正規化と集約（クエリパラメータを除去して集計）
        aggregated_nodes = {}
        base_url_map = {} # full_url -> base_url
        
        for url_obj in self.data.urls:
            # PDFや画像は除外
            if any(url_obj.url.lower().endswith(ext) for ext in ['.pdf', '.png', '.jpg', '.jpeg', '.gif']):
                continue
                
            parsed = urlparse(url_obj.url)
            base_url = parsed.scheme + "://" + parsed.netloc + parsed.path
            
            if base_url not in aggregated_nodes:
                aggregated_nodes[base_url] = {
                    "url": base_url,
                    "in_degree": 0,
                    "category": url_obj.get_category(),
                    "obj": url_obj
                }
            
            aggregated_nodes[base_url]["in_degree"] += url_obj.in_degree
            base_url_map[url_obj.url] = base_url

        # グローバルナビゲーション（共通リンク）の判定
        total_pages = len(self.data.urls)
        global_nav_threshold = total_pages * 0.05
        global_nav_urls = set()
        if total_pages > 0:
            global_nav_urls = {u.url for u in self.data.urls if u.in_degree >= global_nav_threshold}

        # ノードの生成
        for base_url, data in aggregated_nodes.items():
            url_obj = data["obj"]
            
            # グローバルナビゲーションに含まれるURLはグラフから除外（ただしトップページは残す）
            if url_obj.url in global_nav_urls and base_url != self.data.source_url.split('?')[0]:
                continue
                
            cat_idx = category_map.get(data["category"], 0)
            
            # ノードサイズを入次数に基づいて動的に設定
            # 基本サイズ10 + 入次数の対数スケール
            import math
            in_degree = data["in_degree"]
            symbol_size = 10 + (math.log(in_degree + 1) * 5)
            symbol_size = min(symbol_size, 50) # 最大サイズ制限
            
            # トップページは特別扱い
            if base_url == self.data.source_url.split('?')[0]:
                symbol_size = 60
                
            # ノード名の生成
            # ドメインを除去し、パスのみを表示
            parsed = urlparse(base_url)
            path = parsed.path
            
            # 末尾のスラッシュを除去して最後のセグメントを取得（ラベル用）
            label_path = path.rstrip('/')
            name = label_path.split('/')[-1]
            
            if not name or base_url == self.data.source_url.split('?')[0]:
                name = 'Top Page'
            
            # カテゴリ名を取得
            category_name = unique_categories[cat_idx] if cat_idx < len(unique_categories) else 'Other'
                
            nodes.append({
                "id": base_url,
                "name": name, # ラベルは短い名前
                "symbolSize": symbol_size,
                "value": in_degree,
                "category": cat_idx,
                "categoryName": category_name,
                "label": {
                    "show": symbol_size > 20
                }
            })
            
        # リンクの生成（集約されたノード間）
        # 全URLのreferrersを見て、base_url間のリンクを作成
        seen_links = set()
        for url_obj in self.data.urls:
            target_base = base_url_map.get(url_obj.url)
            if not target_base or target_base not in aggregated_nodes:
                continue
                
            for referrer in url_obj.referrers:
                source_base = base_url_map.get(referrer)
                if not source_base or source_base not in aggregated_nodes:
                    continue
                
                if source_base != target_base:
                    link_key = (source_base, target_base)
                    if link_key not in seen_links:
                        links.append({
                            "source": source_base,
                            "target": target_base
                        })
                        seen_links.add(link_key)
        
        return json.dumps({
            "nodes": nodes,
            "links": links,
            "categories": categories
        }, ensure_ascii=False)

    def _generate_global_nav_html(self) -> str:
        """グローバルナビゲーション（共通リンク）のHTML生成"""
        total_pages = len(self.data.urls)
        if total_pages == 0:
            return ""
            
        threshold = total_pages * 0.05
        global_nav_items = [u for u in self.data.urls if u.in_degree >= threshold]
        global_nav_items.sort(key=lambda x: x.in_degree, reverse=True)
        
        html_parts = []
        for item in global_nav_items:
            percentage = (item.in_degree / total_pages) * 100
            html_parts.append(f"""
                <div class="category-item" style="border-left-color: #ecc94b;">
                    <div class="category-name"><a href="{item.url}" target="_blank" class="url-link">{item.url}</a></div>
                    <div class="category-count">{item.in_degree:,} <span style="font-size:0.6em; color:#718096;">({percentage:.1f}%)</span></div>
                </div>
            """)
            
        if not html_parts:
            return '<div style="padding:15px; color:#718096;">該当なし</div>'
            
        return '\n'.join(html_parts)

    def _generate_isolated_pages_html(self) -> str:
        """孤立ページのHTML生成"""
        isolated_pages = [
            u for u in self.data.urls 
            if (u.url.endswith('/') or u.url.endswith('index.html')) 
            and u.in_degree <= 2
        ]
        isolated_pages.sort(key=lambda x: x.in_degree)
        
        if not isolated_pages:
            return '<div style="padding:15px; color:#718096;">該当なし</div>'
            
        rows = []
        for u in isolated_pages:
            # Sitemapページへの言及
            note = ""
            if "sitemap" in u.url:
                note = '<span class="badge status-3xx">Check Sitemap</span>'
                
            rows.append(f"""
                <tr>
                    <td><a href="{u.url}" target="_blank" class="url-link">{u.url}</a> {note}</td>
                    <td>{u.in_degree}</td>
                    <td>{u.get_category()}</td>
                </tr>
            """)
            
        return f"""
            <table class="url-table">
                <thead>
                    <tr>
                        <th>URL</th>
                        <th>被リンク数</th>
                        <th>カテゴリ</th>
                    </tr>
                </thead>
                <tbody>
                    {chr(10).join(rows)}
                </tbody>
            </table>
        """
