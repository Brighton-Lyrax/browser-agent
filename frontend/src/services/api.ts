import axios from 'axios'
import { Session, ActionRequest, ActionResponse } from '../types'

const API_BASE = '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const checkHealth = async () => {
  const response = await apiClient.get('/health')
  return response.data
}

export const createSession = async (): Promise<Session> => {
  const response = await apiClient.post('/sessions', {})
  return response.data
}

export const getSession = async (sessionId: string): Promise<Session> => {
  const response = await apiClient.get(`/sessions/${sessionId}`)
  return response.data
}

export const listSessions = async (): Promise<Session[]> => {
  const response = await apiClient.get('/sessions')
  return response.data
}

export const closeSession = async (sessionId: string): Promise<void> => {
  await apiClient.delete(`/sessions/${sessionId}`)
}

export const executeAction = async (
  sessionId: string,
  action: ActionRequest
): Promise<ActionResponse> => {
  const response = await apiClient.post(
    `/sessions/${sessionId}/actions`,
    action
  )
  return response.data
}

export const navigate = async (
  sessionId: string,
  url: string
): Promise<ActionResponse> => {
  const response = await apiClient.post(
    `/sessions/${sessionId}/actions/navigate`,
    { url }
  )
  return response.data
}

export const takeScreenshot = async (sessionId: string): Promise<ActionResponse> => {
  const response = await apiClient.post(
    `/sessions/${sessionId}/actions/screenshot`
  )
  return response.data
}

export default apiClient
