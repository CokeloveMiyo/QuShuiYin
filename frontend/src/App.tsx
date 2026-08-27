import { useEffect, useRef, useState, type ReactNode, type MouseEvent } from 'react'
import { AnimatePresence, motion, useMotionValue, useSpring } from 'framer-motion'
import {
  cleanShareText,
  imageSrc,
  livePhotoSrc,
  parseMedia,
  proxyDownloadUrl,
  proxyStreamUrl,
  type ParseData,
} from './api'
import './App.css'

const PLATFORMS = [
  '抖音',
  '快手',
  'B站',
  'YouTube',
  '小红书',
  'TikTok',
  '微博',
  '西瓜',
]

function MagneticButton({
  children,
  onClick,
  disabled,
  className,
}: {
  children: ReactNode
  onClick?: () => void
  disabled?: boolean
  className?: string
}) {
  const ref = useRef<HTMLButtonElement>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const springX = useSpring(x, { stiffness: 260, damping: 18 })
  const springY = useSpring(y, { stiffness: 260, damping: 18 })

  const onMove = (e: MouseEvent) => {
    const el = ref.current
    if (!el || disabled) return
    const rect = el.getBoundingClientRect()
    const dx = e.clientX - (rect.left + rect.width / 2)
    const dy = e.clientY - (rect.top + rect.height / 2)
    x.set(dx * 0.22)
    y.set(dy * 0.22)
  }

  const onLeave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.button
      ref={ref}
      type="button"
      className={className}
      disabled={disabled}
      style={{ x: springX, y: springY }}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      onClick={onClick}
      whileTap={disabled ? undefined : { scale: 0.96 }}
    >
      {children}
    </motion.button>
  )
}

function App() {
  const [raw, setRaw] = useState('')
  const [detected, setDetected] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ParseData | null>(null)
  const [activeImage, setActiveImage] = useState(0)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const { url } = cleanShareText(raw)
    setDetected(url)
  }, [raw])

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText()
      if (text) {
        setRaw(text)
        textareaRef.current?.focus()
      }
    } catch {
      setError('无法读取剪贴板，请手动粘贴')
    }
  }

  const handleParse = async () => {
    setError(null)
    setResult(null)
    setActiveImage(0)
    const text = raw.trim()
    if (!text) {
      setError('请先粘贴分享链接或文案')
      return
    }
    if (!cleanShareText(text).url) {
      setError('未识别到有效链接，请检查内容')
      return
    }
    setLoading(true)
    try {
      const data = await parseMedia(text)
      setResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : '解析失败')
    } finally {
      setLoading(false)
    }
  }

  const download = (url: string, name: string) => {
    // Prefer ASCII slug so older proxies don't choke; server also sanitizes headers
    const safe = name
      .replace(/[^\w.-]+/g, '_')
      .replace(/^_+|_+$/g, '')
      .slice(0, 60) || 'media'
    const a = document.createElement('a')
    a.href = proxyDownloadUrl(url, safe)
    a.rel = 'noopener'
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  const images = result?.image_list?.filter((i) => imageSrc(i)) ?? []
  const videos =
    result?.video_list?.length
      ? result.video_list
      : result?.video_url
        ? [result.video_url]
        : []

  return (
    <div className="page">
      <header className="topbar">
        <motion.div
          className="brand"
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="brand-mark" aria-hidden />
          <span className="brand-name">清影</span>
        </motion.div>
        <motion.p
          className="top-note"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.25 }}
        >
          仅供学习交流 · 请遵守平台与版权规范
        </motion.p>
      </header>

      <main className="hero">
        <motion.div
          className="hero-copy"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="eyebrow">多平台 · 自动提取 · 预览下载</p>
          <h1>
            粘贴链接
            <br />
            <span>一键拿走干净素材</span>
          </h1>
          <p className="lede">
            分享文案里夹杂文字也没关系，清影会自动揪出链接，解析无水印视频与图集。
          </p>
        </motion.div>

        <motion.section
          className="composer"
          initial={{ opacity: 0, y: 36 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="composer-glow" aria-hidden />
          <label className="field-label" htmlFor="share-input">
            分享链接 / 文案
          </label>
          <textarea
            id="share-input"
            ref={textareaRef}
            className="share-input"
            rows={4}
            placeholder="例如：5.23 复制打开抖音，看看【作者】的作品 https://v.douyin.com/xxxxx/"
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault()
                void handleParse()
              }
            }}
          />

          <AnimatePresence>
            {detected && (
              <motion.div
                className="url-chip"
                initial={{ opacity: 0, y: 8, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 4 }}
                transition={{ type: 'spring', stiffness: 380, damping: 24 }}
              >
                <span className="chip-dot" />
                <span className="chip-label">已识别链接</span>
                <code>{detected}</code>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="actions">
            <button type="button" className="btn ghost" onClick={() => void handlePaste()}>
              粘贴
            </button>
            <button
              type="button"
              className="btn ghost"
              onClick={() => {
                setRaw('')
                setResult(null)
                setError(null)
              }}
            >
              清空
            </button>
            <MagneticButton
              className="btn primary"
              disabled={loading}
              onClick={() => void handleParse()}
            >
              {loading ? (
                <span className="btn-loading">
                  <span className="spinner" />
                  解析中…
                </span>
              ) : (
                '开始解析'
              )}
            </MagneticButton>
          </div>

          <AnimatePresence>
            {error && (
              <motion.p
                className="error"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>
        </motion.section>

        <motion.ul
          className="platforms"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35 }}
        >
          {PLATFORMS.map((name, i) => (
            <motion.li
              key={name}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + i * 0.04 }}
              whileHover={{ y: -3, scale: 1.04 }}
            >
              {name}
            </motion.li>
          ))}
          <li className="more">+18</li>
        </motion.ul>
      </main>

      <AnimatePresence mode="wait">
        {result && (
          <motion.section
            className="result"
            key="result"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ type: 'spring', stiffness: 120, damping: 18 }}
          >
            <div className="result-meta">
              <div className="meta-left">
                {result.author?.avatar ? (
                  <img
                    className="avatar"
                    src={proxyStreamUrl(result.author.avatar)}
                    alt=""
                  />
                ) : (
                  <div className="avatar placeholder" />
                )}
                <div>
                  <p className="platform-tag">{result.platform || '未知平台'}</p>
                  <h2>{result.title || '未命名作品'}</h2>
                  <p className="author">{result.author?.nickname || '未知作者'}</p>
                </div>
              </div>
            </div>

            <div className="preview-grid">
              {videos.length > 0 && (
                <div className="preview-block">
                  <div className="preview-head">
                    <h3>视频预览</h3>
                    <span>{videos.length} 段</span>
                  </div>
                  {videos.map((url, idx) => (
                    <div className="video-card" key={url + idx}>
                      <video
                        controls
                        playsInline
                        poster={
                          result.cover_url
                            ? proxyStreamUrl(result.cover_url)
                            : undefined
                        }
                        src={proxyStreamUrl(url)}
                      />
                      <MagneticButton
                        className="btn primary slim"
                        onClick={() =>
                          download(
                            url,
                            `video_${idx + 1}`,
                          )
                        }
                      >
                        保存视频 {videos.length > 1 ? idx + 1 : ''}
                      </MagneticButton>
                    </div>
                  ))}
                </div>
              )}

              {images.length > 0 && (
                <div className="preview-block">
                  <div className="preview-head">
                    <h3>图集预览</h3>
                    <span>
                      {activeImage + 1} / {images.length}
                    </span>
                  </div>
                  <div className="image-stage">
                    <img src={proxyStreamUrl(imageSrc(images[activeImage]))} alt="" />
                    {livePhotoSrc(images[activeImage]) && (
                      <span className="live-badge">实况</span>
                    )}
                  </div>
                  <div className="thumbs">
                    {images.map((img, i) => (
                      <button
                        key={i}
                        type="button"
                        className={`thumb ${i === activeImage ? 'on' : ''}`}
                        onClick={() => setActiveImage(i)}
                      >
                        <img src={proxyStreamUrl(imageSrc(img))} alt="" />
                      </button>
                    ))}
                  </div>
                  <div className="image-actions">
                    <MagneticButton
                      className="btn primary slim"
                      onClick={() =>
                        download(
                          imageSrc(images[activeImage]),
                          `image_${activeImage + 1}`,
                        )
                      }
                    >
                      保存当前图片
                    </MagneticButton>
                    {livePhotoSrc(images[activeImage]) && (
                      <button
                        type="button"
                        className="btn ghost slim"
                        onClick={() =>
                          download(
                            livePhotoSrc(images[activeImage])!,
                            `live_${activeImage + 1}`,
                          )
                        }
                      >
                        保存实况
                      </button>
                    )}
                    <button
                      type="button"
                      className="btn ghost slim"
                      onClick={() => {
                        images.forEach((img, i) => {
                          setTimeout(() => {
                            download(
                              imageSrc(img),
                              `image_${i + 1}`,
                            )
                          }, i * 350)
                        })
                      }}
                    >
                      全部保存
                    </button>
                  </div>
                </div>
              )}

              {!videos.length && !images.length && result.cover_url && (
                <div className="preview-block">
                  <img
                    className="cover-only"
                    src={proxyStreamUrl(result.cover_url)}
                    alt=""
                  />
                  <p className="empty-hint">未获取到可下载媒体，可尝试其他链接</p>
                </div>
              )}
            </div>

            {result.audio_url && (
              <div className="audio-row">
                <audio controls src={proxyStreamUrl(result.audio_url)} />
                <button
                  type="button"
                  className="btn ghost slim"
                  onClick={() =>
                    download(result.audio_url!, 'audio')
                  }
                >
                  保存音频
                </button>
              </div>
            )}
          </motion.section>
        )}
      </AnimatePresence>

      <footer className="footer">
        <p>清影 Qingying · 仅供学习交流，请遵守平台与版权规范</p>
      </footer>
    </div>
  )
}

export default App
