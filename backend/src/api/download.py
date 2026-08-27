"""Proxy media downloads to bypass hotlink / CORS restrictions."""
from flask import Blueprint, request, Response, stream_with_context
from urllib.parse import urlparse, unquote, quote
import re
import requests
from utils.media_proxy import resolve_referer
from configs.logging_config import logger
from utils.common_utils import make_response

bp = Blueprint('download', __name__)

ALLOWED_SCHEMES = {'http', 'https'}
BLOCKED_HOSTS = {'localhost', '127.0.0.1', '0.0.0.0', '::1'}


def _is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False
        host = (parsed.hostname or '').lower()
        if not host or host in BLOCKED_HOSTS:
            return False
        # Block obvious private / link-local ranges
        if host.startswith('10.') or host.startswith('192.168.') or host.startswith('169.254.'):
            return False
        if host.startswith('172.'):
            parts = host.split('.')
            if len(parts) > 1 and parts[1].isdigit() and 16 <= int(parts[1]) <= 31:
                return False
        return True
    except Exception:
        return False


def _ascii_filename(name: str, ext: str) -> str:
    """HTTP headers must be latin-1; keep a safe ASCII fallback name."""
    base = re.sub(r'[^A-Za-z0-9._-]+', '_', name).strip('._') or 'media'
    base = base[:60]
    if not ext.startswith('.'):
        ext = f'.{ext}' if ext else ''
    if base.lower().endswith(ext.lower()):
        return base
    return f'{base}{ext}'


def _content_disposition(display_name: str, ascii_name: str) -> str:
    # RFC 5987: ascii filename + UTF-8 filename* for browsers that support it
    encoded = quote(display_name)
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{encoded}"


def _guess_ext(url: str, content_type: str) -> str:
    path = urlparse(url).path
    name = unquote(path.rsplit('/', 1)[-1] if path else '')
    name = name.split('?')[0]
    if '.' in name and len(name) < 120:
        ext = name.rsplit('.', 1)[-1].lower()
        if re.fullmatch(r'[a-z0-9]{2,5}', ext):
            return ext
    if 'video' in content_type or 'octet-stream' in content_type:
        return 'mp4'
    if 'image/jpeg' in content_type or 'image/jpg' in content_type:
        return 'jpg'
    if 'image/png' in content_type:
        return 'png'
    if 'image/webp' in content_type:
        return 'webp'
    if 'audio' in content_type or 'mpeg' in content_type:
        return 'mp3'
    return 'bin'


def _upstream_headers(url: str) -> dict:
    referer = resolve_referer(url)
    return {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/122.0.0.0 Safari/537.36'
        ),
        'Referer': referer,
        'Origin': referer.rstrip('/'),
        'Accept': '*/*',
    }


@bp.route('/download', methods=['GET'])
def download():
    url = request.args.get('url', '').strip()
    filename = request.args.get('filename', 'media').strip() or 'media'
    # Keep readable name for filename*, strip path separators only
    filename = re.sub(r'[\\/:*?"<>|\r\n]+', '_', filename).strip()[:80] or 'media'

    if not url or not _is_safe_url(url):
        return make_response(400, '无效的下载地址', None, False), 400

    try:
        headers = _upstream_headers(url)
        upstream = requests.get(url, headers=headers, stream=True, timeout=90, allow_redirects=True)
        if upstream.status_code >= 400:
            logger.error(f'Download upstream failed: {upstream.status_code} {url}')
            return make_response(502, '资源下载失败，请稍后重试', None, False), 502

        content_type = upstream.headers.get('Content-Type', 'application/octet-stream')
        # Force downloadable type when upstream returns HTML/JSON by mistake
        if 'text/html' in content_type or 'application/json' in content_type:
            logger.error(f'Download got non-media content-type: {content_type}')
            return make_response(502, '资源下载失败，链接可能已失效', None, False), 502

        ext = _guess_ext(url, content_type)
        display_name = filename if '.' in filename.rsplit('/', 1)[-1] else f'{filename}.{ext}'
        ascii_name = _ascii_filename(filename, ext)

        def generate():
            for chunk in upstream.iter_content(chunk_size=65536):
                if chunk:
                    yield chunk

        # Prefer a stable media content-type for browsers
        out_type = content_type
        if 'octet-stream' in content_type and ext == 'mp4':
            out_type = 'video/mp4'

        resp = Response(stream_with_context(generate()), content_type=out_type)
        resp.headers['Content-Disposition'] = _content_disposition(display_name, ascii_name)
        resp.headers['Cache-Control'] = 'no-store'
        return resp
    except Exception:
        logger.exception('Download Error')
        return make_response(500, '下载失败，请稍后再试', None, False), 500


@bp.route('/stream', methods=['GET'])
def stream():
    """Inline media stream for browser preview (bypasses hotlink)."""
    url = request.args.get('url', '').strip()
    if not url or not _is_safe_url(url):
        return make_response(400, '无效的媒体地址', None, False), 400

    try:
        headers = _upstream_headers(url)
        range_header = request.headers.get('Range')
        if range_header:
            headers['Range'] = range_header

        upstream = requests.get(url, headers=headers, stream=True, timeout=90, allow_redirects=True)
        if upstream.status_code >= 400:
            return make_response(502, '媒体加载失败', None, False), 502

        content_type = upstream.headers.get('Content-Type', 'application/octet-stream')

        def generate():
            for chunk in upstream.iter_content(chunk_size=65536):
                if chunk:
                    yield chunk

        resp = Response(
            stream_with_context(generate()),
            status=upstream.status_code,
            content_type=content_type,
        )
        for key in ('Content-Length', 'Content-Range', 'Accept-Ranges'):
            if key in upstream.headers:
                resp.headers[key] = upstream.headers[key]
        resp.headers['Cache-Control'] = 'private, max-age=300'
        return resp
    except Exception:
        logger.exception('Stream Error')
        return make_response(500, '媒体加载失败', None, False), 500
