import { describe, it, expect, beforeEach } from 'vitest'
import { getToken, setToken, removeToken, getUser, setUser, clearAuth } from '../storage'

beforeEach(() => {
  localStorage.clear()
})

describe('storage — Token', () => {
  it('should return null when no token stored', () => {
    expect(getToken()).toBeNull()
  })

  it('should store and retrieve token', () => {
    setToken('my-jwt-token')
    expect(getToken()).toBe('my-jwt-token')
  })

  it('should remove token', () => {
    setToken('my-jwt-token')
    removeToken()
    expect(getToken()).toBeNull()
  })

  it('should overwrite existing token', () => {
    setToken('token-1')
    setToken('token-2')
    expect(getToken()).toBe('token-2')
  })
})

describe('storage — User', () => {
  it('should return null when no user stored', () => {
    expect(getUser()).toBeNull()
  })

  it('should store and retrieve user', () => {
    const user = { username: 'admin', sys_fullname: '管理员', sys_adm: 'Y' }
    setUser(user)
    expect(getUser()).toEqual(user)
  })

  it('should handle invalid JSON in localStorage gracefully', () => {
    localStorage.setItem('genesis_pc_user', 'not-json')
    expect(getUser()).toBeNull()
  })

  it('should return fresh copy from parse (not reference)', () => {
    const user = { username: 'test', permissions: [{ module: 'vip', read: 'Y' }] }
    setUser(user)
    const retrieved = getUser() as typeof user
    expect(retrieved).toEqual(user)
    retrieved.username = 'mutated'
    expect(getUser()?.username).toBe('test')
  })

  it('should keep user when only token is removed', () => {
    setToken('tok')
    setUser({ username: 'u' })
    removeToken()
    expect(getUser()).toEqual({ username: 'u' })
  })
})

describe('storage — clearAuth', () => {
  it('should clear both token and user', () => {
    setToken('tok')
    setUser({ username: 'u' })
    clearAuth()
    expect(getToken()).toBeNull()
    expect(getUser()).toBeNull()
  })

  it('should not remove unrelated localStorage keys', () => {
    localStorage.setItem('genesis_pc_company', 'test')
    clearAuth()
    expect(localStorage.getItem('genesis_pc_company')).toBe('test')
  })
})
