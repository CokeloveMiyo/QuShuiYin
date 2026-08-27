"""Referer / Origin rules for media proxy requests."""
from urllib.parse import urlparse

# (host keywords, referer)
REFERER_RULES: list[tuple[tuple[str, ...], str]] = [
    (('xhscdn', 'xiaohongshu'), 'https://www.xiaohongshu.com/'),
    (('douyin', 'iesdouyin', 'douyinpic', 'douyinstatic', 'snssdk', 'byteimg', 'bytedance'), 'https://www.douyin.com/'),
    (('kuaishou', 'chenzhongtech', 'kwimgs', 'yximgs', 'gifshow'), 'https://www.kuaishou.com/'),
    (('bilivideo', 'hdslb', 'bilibili', 'b23.tv'), 'https://www.bilibili.com/'),
    (('weibo', 'sinaimg', 'weibocdn'), 'https://weibo.com/'),
    (('zhimg', 'zhihu'), 'https://www.zhihu.com/'),
    (('tiktok', 'tiktokcdn', 'byteoversea'), 'https://www.tiktok.com/'),
    (('googlevideo', 'youtube', 'ytimg', 'ggpht'), 'https://www.youtube.com/'),
    (('ixigua', 'ixiguavideo', 'toutiaovod', 'bytecdn'), 'https://www.ixigua.com/'),
    (('qpic', 'weishi'), 'https://weishi.qq.com/'),
    (('pearvideo',), 'https://www.pearvideo.com/'),
    (('acfun', 'kscdn', 'ksyun'), 'https://www.acfun.cn/'),
    (('pipigx', 'pipix', 'xiaochuankeji'), 'https://www.pipix.com/'),
    (('meipai',), 'https://www.meipai.com/'),
    (('huya', 'yy.com'), 'https://www.huya.com/'),
    (('xinpianchang',), 'https://www.xinpianchang.com/'),
    (('haokan', 'hao123'), 'https://haokan.baidu.com/'),
    (('baidu', 'bdstatic', 'bdimg'), 'https://www.baidu.com/'),
    (('instagram', 'cdninstagram', 'fbcdn'), 'https://www.instagram.com/'),
    (('facebook',), 'https://www.facebook.com/'),
    (('twitter', 'twimg', 'x.com'), 'https://x.com/'),
]


def resolve_referer(url: str) -> str:
    host = (urlparse(url).hostname or '').lower()
    for keywords, referer in REFERER_RULES:
        if any(k in host for k in keywords):
            return referer
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f'{parsed.scheme}://{parsed.netloc}/'
    return 'https://www.google.com/'
