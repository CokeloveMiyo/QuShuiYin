import re
import json
import os
from urllib.parse import urlparse, parse_qs, urlencode
from src.parsers.base_parser import BaseParser
from configs.logging_config import get_logger
import requests

logger = get_logger(__name__)

NOTE_ID_RE = re.compile(r'/(?:explore|discovery/item)/([0-9a-fA-F]+)')
INITIAL_STATE_RE = re.compile(
    r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*(?:</script>|;?\s*window\.)',
    re.DOTALL,
)


class XiaohongshuParser(BaseParser):
    def __init__(self, real_url):
        super().__init__(real_url)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/128.0.0.0 Safari/537.36'
            ),
            'Referer': 'https://www.xiaohongshu.com/',
        }
        cookie = os.getenv('XIAOHONGSHU_COOKIE')
        if cookie:
            self.headers['Cookie'] = cookie

        self.note_id = self._extract_note_id(real_url)
        html_content = self.fetch_html_content()
        self.note_data = self._parse_note_data(html_content)

    @staticmethod
    def _extract_note_id(url: str) -> str | None:
        match = NOTE_ID_RE.search(url or '')
        return match.group(1) if match else None

    @staticmethod
    def _normalize_url(url: str | None) -> str | None:
        if not url:
            return None
        url = url.replace('\\u002F', '/').replace('\\/', '/')
        if url.startswith('//'):
            return 'https:' + url
        return url

    def fetch_html_content(self):
        try:
            resp = self.session.get(self.real_url, headers=self.headers, timeout=12, allow_redirects=True)
            resp.raise_for_status()
            final_url = resp.url or ''
            if 'xiaohongshu.com/login' in final_url:
                logger.error('小红书：未配置有效 Cookie，请求被重定向到登录页')
            elif 'xiaohongshu.com/404' in final_url:
                logger.error('小红书：页面不存在或被风控拦截（404）')
            self.html_content = resp.text
            return self.html_content
        except requests.RequestException as e:
            logger.error(f'Failed to get the page: {self.real_url}, Error: {e}')
            return None

    def _parse_note_data(self, html_content) -> dict:
        if not html_content or 'noteDetailMap' not in html_content:
            return {}

        json_str = None
        match = INITIAL_STATE_RE.search(html_content)
        if match:
            json_str = match.group(1)
        else:
            json_str = BaseParser.parse_html_data(
                html_content,
                re.compile(r'window\.__INITIAL_STATE__\s*=\s*(\{.*\})', re.DOTALL),
            )

        if not json_str:
            return {}

        try:
            cleaned = json_str.replace(':undefined', ':null').replace('undefined', 'null')
            full_data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f'小红书 JSON 解析失败: {e}')
            return {}

        note_root = full_data.get('note', {})
        detail_map = note_root.get('noteDetailMap') or {}

        # 优先按 URL 中的 note_id 查找
        if self.note_id and self.note_id in detail_map:
            note = detail_map[self.note_id].get('note') or {}
            if note:
                return note

        # 回退：firstNoteId 或 map 中第一个有效 note
        first_note_id = note_root.get('firstNoteId')
        if first_note_id and first_note_id in detail_map:
            note = detail_map[first_note_id].get('note') or {}
            if note:
                return note

        for item in detail_map.values():
            note = (item or {}).get('note') or {}
            if note.get('video') or note.get('imageList'):
                return note

        return {}

    @staticmethod
    def _pick_stream_url(stream_obj: dict | None) -> str | None:
        if not isinstance(stream_obj, dict):
            return None
        for codec in ('h264', 'h265', 'av1'):
            entries = stream_obj.get(codec) or []
            if entries and isinstance(entries[0], dict):
                for key in ('masterUrl', 'backupUrl', 'url'):
                    url = entries[0].get(key)
                    if url:
                        return url
        return None

    def get_author_info(self):
        user = self.note_data.get('user', {})
        return {
            'nickname': user.get('nickname', ''),
            'author_id': user.get('userId', ''),
            'avatar': self._normalize_url(user.get('avatar', '')),
        }

    def get_real_video_url(self):
        video_info = self.note_data.get('video') or {}
        media = video_info.get('media') or {}
        stream = media.get('stream') or {}
        url = self._pick_stream_url(stream)
        if url:
            return self._normalize_url(url)

        # 部分笔记把 consumer 字段作为备用
        consumer = video_info.get('consumer') or {}
        for key in ('originVideoKey', 'origin_video_key', 'videoKey'):
            if consumer.get(key):
                return self._normalize_url(consumer.get(key))
        return None

    def get_title_content(self):
        title = self.note_data.get('title', '')
        desc = self.note_data.get('desc', '')
        return f'{title}\n{desc}'.strip()

    def get_cover_photo_url(self):
        image_list = self.note_data.get('imageList') or []
        if not image_list:
            return None
        first = image_list[0] if isinstance(image_list[0], dict) else {}
        for key in ('urlDefault', 'urlPre', 'url'):
            url = self._normalize_url(first.get(key))
            if url:
                return url
        return None

    def get_image_list(self):
        image_url_list = []
        image_list = self.note_data.get('imageList') or []
        for image in image_list:
            if not isinstance(image, dict):
                continue
            url = None
            for key in ('urlDefault', 'urlPre', 'url'):
                url = self._normalize_url(image.get(key))
                if url:
                    break
            if not url:
                continue

            if image.get('livePhoto'):
                stream = image.get('stream') or {}
                live_url = self._pick_stream_url(stream)
                if live_url:
                    image_url_list.append({'url': url, 'live_photo_url': self._normalize_url(live_url)})
                    continue
            image_url_list.append(url)
        return image_url_list
