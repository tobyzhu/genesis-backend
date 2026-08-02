/** PC 主题预设与应用 */

export const THEME_IDS = ['azure', 'salon', 'moss'] as const
export type ThemeId = (typeof THEME_IDS)[number]

export const THEME_OPTIONS: { id: ThemeId; label: string }[] = [
  { id: 'azure', label: '静海蓝' },
  { id: 'salon', label: '雾玫瑰' },
  { id: 'moss', label: '松烟绿' },
]

export const THEME_STORAGE_KEY = 'genesis_pc_theme'
export const DEFAULT_THEME: ThemeId = 'azure'

export function normalizeThemeId(raw: string | null | undefined): ThemeId {
  if (raw && (THEME_IDS as readonly string[]).includes(raw)) return raw as ThemeId
  return DEFAULT_THEME
}

export function applyTheme(themeId: ThemeId | string) {
  const id = normalizeThemeId(themeId)
  document.documentElement.setAttribute('data-theme', id)
  return id
}

export function loadStoredTheme(): ThemeId {
  try {
    return normalizeThemeId(localStorage.getItem(THEME_STORAGE_KEY))
  } catch {
    return DEFAULT_THEME
  }
}
