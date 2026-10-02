#!/usr/bin/env python3
"""Rebuild the static blog homepage from reports/*.html; no dependencies."""
from collections import Counter
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title_done = False
        self.title = ''
        self.description = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title' and not self.title_done:
            self.in_title = True
        if tag == 'meta' and attrs.get('name', '').lower() == 'description':
            self.description = attrs.get('content', '')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
            self.title_done = True

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def collect_reports(root):
    reports = []
    for path in (root / 'reports').glob('*.html'):
        match = re.fullmatch(r'(\d{4}-\d{2}-\d{2})(?:-(\d{6}))?\.html', path.name)
        if not match:
            continue
        day, stamp = match.groups()
        date.fromisoformat(day)
        if stamp and not (int(stamp[:2]) < 24 and int(stamp[2:4]) < 60 and int(stamp[4:]) < 60):
            raise ValueError(f'Invalid report time: {path.name}')
        metadata = Metadata()
        metadata.feed(path.read_text(encoding='utf-8'))
        reports.append(dict(date=day, time=stamp or '', path=f'reports/{path.name}',
                            title=metadata.title.strip() or f'{day} 每日交易報告',
                            description=metadata.description.strip() or '閱讀完整市場研究與交易計畫。'))
    return sorted(reports, key=lambda r: (r['date'], r['time']), reverse=True)


def render(root):
    reports = collect_reports(root)
    articles = []
    seen_months = set()
    for i, report in enumerate(reports):
        month = report['date'][:7]
        anchor = f' id="month-{month}"' if month not in seen_months else ''
        seen_months.add(month)
        latest = '<span class="latest">最新文章</span>' if i == 0 else ''
        title = escape(report['title'])
        description = escape(report['description'])
        url = escape(report['path'], quote=True)
        day = report['date']
        stamp = report['time']
        time_label = f' · {stamp[:2]}:{stamp[2:4]}:{stamp[4:]}' if stamp else ''
        articles.append(f'<li class="entry year-anchor"{anchor}><article>'
                        f'<div class="date"><time datetime="{day}">{day}{time_label}</time>{latest}</div>'
                        f'<h2><a href="{url}">{title}</a></h2><p>{description}</p>'
                        f'<a class="read" href="{url}" aria-label="閱讀 {title}">閱讀完整報告 <span aria-hidden="true">↗</span></a>'
                        '</article></li>')
    months = Counter(r['date'][:7] for r in reports)
    archives = ''.join(f'<a class="archive-link" href="#month-{m}">{m[:4]} 年 {int(m[5:])} 月 <span>{count} 篇</span></a>' for m, count in months.items())
    template = (root / 'templates/index.html').read_text(encoding='utf-8')
    return template.replace('<!--COUNT-->', str(len(reports))).replace('<!--ARTICLES-->', '\n'.join(articles) or '<li class="empty">尚無研究報告。</li>').replace('<!--ARCHIVES-->', archives or '<p>尚無歸檔</p>')


if __name__ == '__main__':
    (ROOT / 'index.html').write_text(render(ROOT), encoding='utf-8')
    print(f'Updated index.html: {len(collect_reports(ROOT))} reports, newest first.')
