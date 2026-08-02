import { describe, it, expect, beforeEach } from 'vitest'
import {
  applyTheme,
  loadStoredTheme,
  normalizeThemeId,
  THEME_STORAGE_KEY,
  DEFAULT_THEME,
} from '../theme'

beforeEach(() => {
  localStorage.clear()
  document.documentElement.removeAttribute('data-theme')
})

describe('theme helpers', () => {
  it('normalizes unknown ids to default', () => {
    expect(normalizeThemeId('nope')).toBe(DEFAULT_THEME)
    expect(normalizeThemeId('salon')).toBe('salon')
  })

  it('applyTheme sets data-theme on html', () => {
    expect(applyTheme('moss')).toBe('moss')
    expect(document.documentElement.getAttribute('data-theme')).toBe('moss')
  })

  it('loadStoredTheme reads localStorage', () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'salon')
    expect(loadStoredTheme()).toBe('salon')
  })
})
