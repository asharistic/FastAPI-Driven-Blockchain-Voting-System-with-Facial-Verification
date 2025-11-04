import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import './Management.css'

function ElectionsManagement() {
  const [elections, setElections] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    loadElections()
  }, [])

  const loadElections = async () => {
    try {
      const response = await adminAPI.getElections()
      setElections(response.data.elections || [])
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load elections.' })
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await adminAPI.createElection({
        ...formData,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString(),
      })
      setMessage({ type: 'success', text: 'Election created successfully!' })
      setShowForm(false)
      setFormData({ title: '', description: '', start_time: '', end_time: '' })
      loadElections()
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to create election.' })
    }
  }

  const handleDelete = async (id) => {
    const election = elections.find(e => e.id === id)
    const confirmMessage = election 
      ? `Are you sure you want to delete "${election.title}"?\n\nThis will also delete ALL candidates associated with this election. This action cannot be undone.`
      : 'Are you sure you want to delete this election? This will also delete all associated candidates.'
    
    if (!window.confirm(confirmMessage)) return
    
    try {
      const response = await adminAPI.deleteElection(id)
      const deletedCount = response.data.deleted_candidates || 0
      let message = 'Election deleted successfully!'
      if (deletedCount > 0) {
        message += ` ${deletedCount} candidate(s) also deleted.`
      }
      setMessage({ type: 'success', text: message })
      loadElections()
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to delete election.' })
    }
  }

  if (loading) return <div className="loading-state">Loading elections...</div>

  return (
    <div className="management-page">
      <div className="management-header">
        <h2>Elections Management</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
          <i className="fas fa-plus"></i> {showForm ? 'Cancel' : 'New Election'}
        </button>
      </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="card form-card">
          <h3>Create New Election</h3>
          <div className="form-group">
            <label className="label">Title</label>
            <input
              type="text"
              className="input"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="label">Description</label>
            <textarea
              className="input"
              rows="3"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="label">Start Time</label>
              <input
                type="datetime-local"
                className="input"
                required
                value={formData.start_time}
                onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="label">End Time</label>
              <input
                type="datetime-local"
                className="input"
                required
                value={formData.end_time}
                onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
              />
            </div>
          </div>
          <button type="submit" className="btn btn-primary">Create Election</button>
        </form>
      )}

      <div className="items-list">
        {elections.length === 0 ? (
          <p className="empty-state">No elections created yet.</p>
        ) : (
          elections.map((election) => (
            <div key={election.id} className="item-card">
              <div className="item-content">
                <h3>{election.title}</h3>
                <p className="item-description">{election.description || 'No description'}</p>
                <div className="item-meta">
                  <span>Start: {new Date(election.start_time).toLocaleString()}</span>
                  <span>End: {new Date(election.end_time).toLocaleString()}</span>
                </div>
                <span className={`status-badge ${election.is_active ? 'active' : 'inactive'}`}>
                  {election.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <button
                onClick={() => handleDelete(election.id)}
                className="btn-delete"
              >
                <i className="fas fa-trash"></i>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ElectionsManagement

