import { describe, it, expect } from 'vitest'
import { computeBookingStats, buildTimeline } from '@/utils/dashboard'

describe('dashboard utils', () => {
  it('computes booking stats from real bookings', () => {
    const bookings = [
      { status: '100' },
      { status: '200' },
      { status: '220' },
      { status: '230' },
      { status: '390' },
    ]
    const stats = computeBookingStats(bookings)
    expect(stats.total).toBe(5)
    expect(stats.pending).toBe(1)
    expect(stats.arrived).toBe(1)
    expect(stats.inStore).toBe(3)
    expect(stats.completed).toBe(1)
    expect(stats.cancelled).toBe(1)
  })

  it('builds a time-sorted timeline without cancelled bookings', () => {
    const timeline = buildTimeline([
      { id: 1, status: '220', start_time: '14:00:00', vname: 'A', mtcode: '13800000001', employee_name: 'E1' },
      { id: 2, status: '100', start_time: '09:30:00', vname: 'B', employee_name: 'E2' },
      { id: 3, status: '390', start_time: '10:00:00', vname: 'C' },
    ])
    expect(timeline).toHaveLength(2)
    expect(timeline[0].time).toBe('09:30')
    expect(timeline[1].time).toBe('14:00')
    expect(timeline[0].statusLabel).toBe('未到店')
    expect(timeline[0].statusColor).toContain('g-color-warning')
  })
})
