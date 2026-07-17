import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSession, navigate, executeAction, takeScreenshot } from '../services/api'
import { useSessionStore } from '../stores/sessionStore'
import { Session, ActionRequest } from '../types'

function SessionPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate_router = useNavigate()
  const { setError, error } = useSessionStore()
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const [screenshot, setScreenshot] = useState<string | null>(null)
  const [url, setUrl] = useState('')
  const [selector, setSelector] = useState('')
  const [text, setText] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    if (sessionId) {
      loadSession()
    }
  }, [sessionId])

  const loadSession = async () => {
    try {
      setLoading(true)
      const data = await getSession(sessionId!)
      setSession(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session')
      navigate_router('/')
    } finally {
      setLoading(false)
    }
  }

  const handleNavigate = async () => {
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    try {
      setActionLoading(true)
      const result = await navigate(sessionId!, url)
      if (result.status === 'success') {
        setSession(prev => prev ? { ...prev, current_url: url } : null)
        handleTakeScreenshot()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Navigation failed')
    } finally {
      setActionLoading(false)
    }
  }

  const handleTakeScreenshot = async () => {
    try {
      const result = await takeScreenshot(sessionId!)
      if (result.result?.screenshot) {
        setScreenshot(result.result.screenshot)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Screenshot failed')
    }
  }

  const handleClick = async () => {
    if (!selector.trim()) {
      setError('Please enter a CSS selector')
      return
    }

    try {
      setActionLoading(true)
      const request: ActionRequest = {
        action_type: 'click',
        parameters: { selector },
      }
      await executeAction(sessionId!, request)
      handleTakeScreenshot()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Click action failed')
    } finally {
      setActionLoading(false)
    }
  }

  const handleType = async () => {
    if (!selector.trim() || !text.trim()) {
      setError('Please enter both selector and text')
      return
    }

    try {
      setActionLoading(true)
      const request: ActionRequest = {
        action_type: 'type',
        parameters: { selector, text },
      }
      await executeAction(sessionId!, request)
      handleTakeScreenshot()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Type action failed')
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-600">Loading session...</div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600">Session not found</div>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Control Panel */}
      <div className="col-span-1 space-y-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Session Control</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-3 py-2 rounded mb-4 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            {/* Navigate */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Navigate to URL
              </label>
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleNavigate}
                disabled={actionLoading}
                className="mt-2 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition"
              >
                Navigate
              </button>
            </div>

            {/* Click */}
            <div className="border-t pt-4">
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Click Element
              </label>
              <input
                type="text"
                value={selector}
                onChange={(e) => setSelector(e.target.value)}
                placeholder="CSS selector (e.g., .button, #id)"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleClick}
                disabled={actionLoading}
                className="mt-2 w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition"
              >
                Click
              </button>
            </div>

            {/* Type */}
            <div className="border-t pt-4">
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Type Text
              </label>
              <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Text to type"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleType}
                disabled={actionLoading}
                className="mt-2 w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition"
              >
                Type
              </button>
            </div>

            {/* Screenshot */}
            <div className="border-t pt-4">
              <button
                onClick={handleTakeScreenshot}
                disabled={actionLoading}
                className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded transition"
              >
                Take Screenshot
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Preview */}
      <div className="col-span-2">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Browser Preview</h2>
          
          {session.current_url && (
            <p className="text-sm text-gray-600 mb-4">
              Current URL: <span className="font-mono text-blue-600">{session.current_url}</span>
            </p>
          )}

          {screenshot ? (
            <div className="bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={`data:image/png;base64,${screenshot}`}
                alt="Browser screenshot"
                className="w-full"
              />
            </div>
          ) : (
            <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center">
              <div className="text-center">
                <p className="text-gray-600 mb-4">No screenshot yet</p>
                <button
                  onClick={handleTakeScreenshot}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition"
                >
                  Take First Screenshot
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default SessionPage
