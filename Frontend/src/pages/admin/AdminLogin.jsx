import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../../services/api'
import './AdminLogin.css'

function AdminLogin() {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authAPI.login(credentials)
      localStorage.setItem('admin_token', response.data.access_token)
      navigate('/admin')
    } catch (err) {
      console.error('Login error:', err)
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        setError('Cannot connect to backend server. Please make sure the backend is running on http://127.0.0.1:5000')
      } else if (err.response?.status === 401) {
        setError('Incorrect username or password. Please try again.')
      } else {
        setError(err.response?.data?.detail || err.message || 'Login failed. Please check your credentials.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <div className="icon">🔐</div>
            <h1>Admin Access</h1>
            <p>Blockchain Voting System</p>
          </div>
          
          <div className="login-body">
            <form onSubmit={handleSubmit}>
              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}
              
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  required
                  placeholder="Enter your username"
                  value={credentials.username}
                  onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                  className="input"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  required
                  placeholder="Enter your password"
                  value={credentials.password}
                  onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                  className="input"
                />
              </div>
              
              <button type="submit" className="btn-login" disabled={loading}>
                {loading ? <span className="loading"></span> : 'Sign In'}
              </button>
            </form>
            
            <a href="/" className="back-link">← Back to Home</a>
            
            <div className="credential-hint">
              Default: admin / admin123
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminLogin

