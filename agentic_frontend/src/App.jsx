import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [backendData, setBackendData] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

  // Fetch backend test data
  const fetchBackendData = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${API_BASE_URL}/api/test`)
      if (!response.ok) throw new Error('Failed to fetch')
      const data = await response.json()
      setBackendData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Fetch users from backend
  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${API_BASE_URL}/api/users`)
      if (!response.ok) throw new Error('Failed to fetch users')
      const data = await response.json()
      setUsers(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBackendData()
    fetchUsers()
  }, [])

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Agentic Microservices</h1>
      
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>

      {/* Backend Connection Status */}
      <div className="card">
        <h2>Backend Connection</h2>
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        {backendData && (
          <div>
            <p>✅ Connected to backend!</p>
            <p>Message: {backendData.message}</p>
            <p>Timestamp: {new Date(backendData.timestamp).toLocaleString()}</p>
          </div>
        )}
        <button onClick={fetchBackendData} disabled={loading}>
          Test Backend Connection
        </button>
      </div>

      {/* Users List */}
      <div className="card">
        <h2>Users from Backend</h2>
        {users.length > 0 ? (
          <ul style={{ textAlign: 'left' }}>
            {users.map(user => (
              <li key={user.id}>
                <strong>{user.name}</strong> - {user.email}
              </li>
            ))}
          </ul>
        ) : (
          <p>No users found</p>
        )}
        <button onClick={fetchUsers} disabled={loading}>
          Refresh Users
        </button>
      </div>

      <p className="read-the-docs">
        This is a microservices architecture with React frontend and Express backend
      </p>
    </>
  )
}

export default App
