import axios from 'axios'

export interface ApiErrorPayload {
  detail?: string
}

const apiClient = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const getApiErrorMessage = (error: unknown, fallback: string) => {
  if (axios.isAxiosError<ApiErrorPayload>(error)) {
    return error.response?.data?.detail || fallback
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}

export default apiClient

