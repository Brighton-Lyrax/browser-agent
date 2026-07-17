import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createSession, listSessions, closeSession } from '../services/api'
import { useSessionStore } from '../stores/sessionStore'
import { Session } from '../types'

function Dashboard() {
  const navigate = useNavigate()
  const { setSessions, setLoading, setError, error } = useSessionStore()
  const [sessions, setSessions_local] = useState<Session[]>([])
  const [loading, setLoading_local] = useState(true)

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setLoading_local(true)
      const data = await listSessions()
      setSessions_local(data)
      setSessions(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions')
    } finally {
      setLoading_local(false)
    }
  }

  const handleCreateSession = async () => {
    try {
      setLoading(true)
      const session = await createSession()
      navigate(`/session/${session.session_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session')
    } finally {
      setLoading(false)
    }
  }

  const handleCloseSession = async (sessionId: string) => {
    try {
      await closeSession(sessionId)
      loadSessions()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to close session')
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Browser Agent</h1>
          <p className="text-gray-600 mt-2">Autonomous browser automation with human-like actions</p>
        </div>
        <button
          onClick={handleCreateSession}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition"
        >
          + New Session
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="text-gray-600">Loading sessions...</div>
        </div>
      ) : sessions.length === 0 ? (
        <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Active Sessions</h3>
          <p className="text-gray-600 mb-4">Create a new session to start automating browser tasks.</p>
          <button
            onClick={handleCreateSession}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg inline-block transition"
          >
            Create First Session
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition border border-gray-200"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {session.session_id.slice(0, 8)}...
                  </h3>
                  <p className="text-sm text-gray-600 mb-1">
                    Status: {session.is_active ? (
                      <span className="text-green-600 font-semibold">Active</span>
                    ) : (
                      <span className="text-red-600 font-semibold">Inactive</span>
                    )}
                  </p>
                  {session.current_url && (
                    <p className="text-sm text-gray-600 truncate">
                      URL: <span className="font-mono text-blue-600">{session.current_url}</span>
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    Created: {new Date(session.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigate(`/session/${session.session_id}`)}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition text-sm"
                  >
                    Open
                  </button>
                  <button
                    onClick={() => handleCloseSession(session.session_id)}
                    className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition text-sm"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard
