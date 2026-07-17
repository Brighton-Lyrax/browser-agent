export interface Session {
  session_id: string
  created_at: string
  is_active: boolean
  current_url?: string
}

export interface ActionResult {
  success: boolean
  message?: string
  error?: string
  [key: string]: any
}

export interface ActionResponse {
  action_id: string
  session_id: string
  action_type: string
  status: 'pending' | 'executing' | 'success' | 'failed'
  result?: ActionResult
  error?: string
  created_at: string
  completed_at?: string
}

export type ActionType = 
  | 'navigate'
  | 'click'
  | 'type'
  | 'scroll'
  | 'screenshot'
  | 'get_content'
  | 'execute_js'
  | 'wait_for_element'

export interface ActionRequest {
  action_type: ActionType
  parameters: Record<string, any>
  description?: string
}
