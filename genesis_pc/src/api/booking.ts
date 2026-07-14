import request from './request'
import type { PageResponse, Booking } from '@/types'

export function getBookingList(params?: Record<string, any>) {
  return request.get<PageResponse<Booking>>('/booking/events/', { params })
}

export function createBooking(data: Partial<Booking>) {
  return request.post<Booking>('/booking/events/', data)
}

export function updateBooking(id: number, data: Partial<Booking>) {
  return request.put<Booking>(`/booking/events/${id}/`, data)
}

export function cancelBooking(id: number) {
  return request.post(`/booking/events/${id}/cancel/`)
}

/** 技师排班 */
export function getEmployeeSchedule(params?: Record<string, any>) {
  return request.get('/adviser/timesets/', { params })
}
