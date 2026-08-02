import { BOOKING_STATUS_MAP } from '@/types'

export interface DashboardBookingStats {
  total: number
  pending: number
  arrived: number
  inStore: number
  completed: number
  cancelled: number
}

const IN_STORE_STATUS = ['200', '210', '220', '230', '240', '250', '260', '270']

export function computeBookingStats(bookings: any[]): DashboardBookingStats {
  const stats: DashboardBookingStats = {
    total: bookings.length,
    pending: 0,
    arrived: 0,
    inStore: 0,
    completed: 0,
    cancelled: 0,
  }
  for (const b of bookings) {
    const s = String(b?.status || '')
    if (s === '100') stats.pending += 1
    if (s === '200') stats.arrived += 1
    if (IN_STORE_STATUS.includes(s)) stats.inStore += 1
    if (s === '230') stats.completed += 1
    if (s === '390') stats.cancelled += 1
  }
  return stats
}

export interface DashboardTimelineItem {
  id: number
  vname: string
  mtcode: string
  time: string
  statusLabel: string
  statusColor: string
  employee: string
}

export function buildTimeline(bookings: any[]): DashboardTimelineItem[] {
  return bookings
    .filter((b) => String(b?.status) !== '390')
    .map((b) => {
      const status = String(b?.status || '')
      const meta = BOOKING_STATUS_MAP[status] || { label: status || '--', color: 'var(--g-color-text-muted)' }
      return {
        id: b?.id,
        vname: b?.vname || '--',
        mtcode: b?.mtcode || '',
        time: String(b?.start_time || '').slice(0, 5),
        statusLabel: meta.label,
        statusColor: meta.color,
        employee: b?.employee_name || '--',
      }
    })
    .sort((a, b) => a.time.localeCompare(b.time))
}
