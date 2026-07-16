import { describe, it, expect, beforeEach } from 'vitest'
import { getCache, setCache, clearCache, cacheKey } from '../cache'

describe('cache utility', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('should store and retrieve data', () => {
    setCache('test-key', { name: 'test' }, 60000)
    const result = getCache('test-key')
    expect(result).toEqual({ name: 'test' })
  })

  it('should return null for expired data', () => {
    setCache('expired-key', 'data', -1000) // already expired
    const result = getCache('expired-key')
    expect(result).toBeNull()
  })

  it('should generate consistent cache keys', () => {
    const key1 = cacheKey('/api/test', { a: '1', b: '2' })
    const key2 = cacheKey('/api/test', { b: '2', a: '1' }) // different order
    expect(key1).toBe(key2)
  })

  it('should clear by prefix', () => {
    setCache('pref_key1', 'v1', 60000)
    setCache('pref_key2', 'v2', 60000)
    setCache('other_key', 'v3', 60000)
    clearCache('pref_')
    expect(getCache('pref_key1')).toBeNull()
    expect(getCache('pref_key2')).toBeNull()
    expect(getCache('other_key')).toBe('v3')
  })
})
