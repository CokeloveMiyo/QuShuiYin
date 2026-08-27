export type Author = {
  nickname?: string
  author_id?: string
  avatar?: string
}

export type ImageItem =
  | string
  | {
      url?: string
      live_photo_url?: string
    }

export type ParseData = {
  video_id?: string
  platform?: string
  title?: string
  video_url?: string | null
  video_list?: string[]
  audio_url?: string | null
  cover_url?: string | null
  author?: Author
  image_list?: ImageItem[]
}

export type ParseResponse = {
  retcode: number
  retdesc: string
  data: ParseData | null
  succ: boolean
}

const URL_RE =
  /https?:\/\/[^\s<>"{}|\\^`\[\]]+/gi

export function extractUrl(text: string): string | null {
  const matches = text.match(URL_RE)
  if (!matches?.length) return null
  // Prefer known short / share domains order by first match after cleanup
  return matches[0].replace(/[),.;!?，。；！？]+$/, '')
}

export function cleanShareText(text: string): { url: string | null; cleaned: string } {
  const url = extractUrl(text)
  if (!url) return { url: null, cleaned: text.trim() }
  return { url, cleaned: url }
}

/** 生产环境填后端地址，如 https://qingying-api.onrender.com ；本地开发留空走 Vite 代理 */
const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') || ''

function apiUrl(path: string): string {
  return `${API_BASE}${path}`
}

export async function parseMedia(text: string): Promise<ParseData> {
  const res = await fetch(apiUrl('/api/parse'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  const json = (await res.json()) as ParseResponse
  if (!json.succ || !json.data) {
    throw new Error(json.retdesc || '解析失败')
  }
  return json.data
}

export function proxyDownloadUrl(url: string, filename: string): string {
  const normalized = normalizeMediaUrl(url)
  if (isLocalMediaUrl(normalized)) return apiUrl(normalized)
  const params = new URLSearchParams({ url: normalized, filename })
  return apiUrl(`/api/download?${params.toString()}`)
}

export function proxyStreamUrl(url: string): string {
  const normalized = normalizeMediaUrl(url)
  if (isLocalMediaUrl(normalized)) return apiUrl(normalized)
  const params = new URLSearchParams({ url: normalized })
  return apiUrl(`/api/stream?${params.toString()}`)
}

function normalizeMediaUrl(url: string): string {
  if (!url) return url
  if (url.startsWith('//')) return `https:${url}`
  return url
}

function isLocalMediaUrl(url: string): boolean {
  return url.startsWith('/static/') || url.startsWith('/api/')
}

export function imageSrc(item: ImageItem): string {
  return typeof item === 'string' ? item : item.url || ''
}

export function livePhotoSrc(item: ImageItem): string | null {
  if (typeof item === 'string') return null
  return item.live_photo_url || null
}
