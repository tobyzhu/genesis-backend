import request from './request'
import type { PageResponse, Booking, BookingEmployee, BookingRoom, BookingInstrument, BookingSchedule, BookingTimeset, ConflictInfo, StatusChangeResult } from '@/types'

export function getBookingList(params?: Record<string, any>) {
  return request.get<{count: number, results: Booking[]}>('/booking/events/', { params })
}

export function createBooking(data: Partial<Booking>) {
  return request.post<Booking>('/booking/events/create/', data)
}

export function updateBooking(id: number, data: Partial<Booking>) {
  return request.put<{status: string}>(`/booking/events/${id}/update/`, data)
}

export function cancelBooking(id: number) {
  return request.post(`/booking/events/${id}/cancel/`)
}

/** 变更预约状态 */
export function changeBookingStatus(id: number, status: string) {
  return request.post<StatusChangeResult>(`/booking/events/${id}/status/`, { status })
}

/** 查询预约明细 */
export function getBookingDetail(id: number) {
  return request.get<Booking>(`/booking/events/${id}/`)
}

/** 冲突检测 */
export function checkBookingConflicts(id: number, params?: Record<string, any>) {
  return request.get<{conflicts: ConflictInfo[]}>(`/booking/events/${id}/check-conflicts/`, { params })
}

/** 时段模板 */
export function getBookingTimesets(params?: Record<string, any>) {
  return request.get<{results: BookingTimeset[]}>('/booking/timesets/', { params })
}

/** 员工排班 */
export function getEmployeeSchedule(params?: Record<string, any>) {
  return request.get<{results: BookingSchedule[]}>('/booking/schedules/', { params })
}

/** 可预约员工 */
export function getBookingEmployees(params?: Record<string, any>) {
  return request.get<{results: BookingEmployee[]}>('/booking/employees/', { params })
}

/** 房间列表 */
export function getBookingRooms(params?: Record<string, any>) {
  return request.get<{results: BookingRoom[]}>('/booking/rooms/', { params })
}

/** 仪器列表 */
export function getBookingInstruments(params?: Record<string, any>) {
  return request.get<{results: BookingInstrument[]}>('/booking/instruments/', { params })
}
/** 批量保存排班 */
export function saveSchedules(data: {schedules: Array<{ecode: string; vsdate: string; scheduleid: string}>}) {
  return request.post<{status: string; saved: number}>('/booking/schedules/save/', data)
}

/** 班次列表 */
export function getShiftList() {
  return request.get<{results: Array<{value: string; label: string}>}>('/booking/schedules/shift-list/')
}
