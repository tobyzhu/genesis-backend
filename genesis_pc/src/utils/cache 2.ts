// ============================================================
// sessionStorage 缓存工具（带 TTL）
// 用于缓存相对固定的基础资料，减少重复 API 请求
// ============================================================

const CACHE_PREFIX = 'genesis_cache_'
const CACHE_VERSION = 'v2'  // 后端数据结构变更时递增

interface CacheEntry<T> {
  data: T
  expireAt: number  // Date.now() + ttl
}

/** 从 sessionStorage 读缓存，过期返回 null */
export function getCache<T>(key: string): T | null {
  try {
    const raw = sessionStorage.getItem(CACHE_PREFIX + CACHE_VERSION + '_' + key)
    if (!raw) return null
    const entry: CacheEntry<T> = JSON.parse(raw)
    if (Date.now() > entry.expireAt) {
      sessionStorage.removeItem(CACHE_PREFIX + CACHE_VERSION + '_' + key)
      return null
    }
    return entry.data
  } catch {
    return null
  }
}

/** 写入 sessionStorage 缓存 */
export function setCache<T>(key: string, data: T, ttlMs: number): void {
  try {
    const entry: CacheEntry<T> = { data, expireAt: Date.now() + ttlMs }
    sessionStorage.setItem(CACHE_PREFIX + CACHE_VERSION + '_' + key, JSON.stringify(entry))
  } catch {
    // sessionStorage 满时静默失败，不影响主流程
  }
}

/** 清空所有缓存（可选按前缀匹配） */
export function clearCache(prefix?: string): void {
  try {
    for (let i = sessionStorage.length - 1; i >= 0; i--) {
      const k = sessionStorage.key(i)
      if (!k || !k.startsWith(CACHE_PREFIX + CACHE_VERSION + '_')) continue
      if (prefix && !k.startsWith(CACHE_PREFIX + CACHE_VERSION + '_' + prefix)) continue
      sessionStorage.removeItem(k)
    }
  } catch {
    // 静默
  }
}

/** 生成一致的缓存 key（URL + 参数） */
export function cacheKey(url: string, params?: Record<string, string>): string {
  if (!params) return url
  const sorted = Object.keys(params).sort().map(k => k + '=' + encodeURIComponent(params[k] || '')).join('&')
  return url + '|' + sorted
}
