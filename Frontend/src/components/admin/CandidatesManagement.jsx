import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import './Management.css'

function CandidatesManagement() {
  const [candidates, setCandidates] = useState([])
  const [elections, setElections] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    candidate_id: '',
    name: '',
    party: '',
    election_id: '',
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    loadCandidates()
    loadElections()
  }, [])

  const loadCandidates = async () => {
    try {
      const response = await adminAPI.getCandidates()
      setCandidates(response.data.candidates || [])
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load candidates.' })
    } finally {
      setLoading(false)
    }
  }

  const loadElections = async () => {
    try {
      const response = await adminAPI.getElections()
      setElections(response.data.elections || [])
    } catch (error) {
      console.error('Failed to load elections:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Check if elections exist
    if (elections.length === 0) {
      setMessage({ 
        type: 'error', 
        text: 'Cannot create candidates without an election. Please create an election first.' 
      })
      return
    }
    
    try {
      // Convert election_id to number if provided
      const submitData = {
        ...formData,
        election_id: formData.election_id ? parseInt(formData.election_id) : null
      }
      
      await adminAPI.createCandidate(submitData)
      setMessage({ type: 'success', text: 'Candidate created successfully!' })
      setShowForm(false)
      setFormData({ candidate_id: '', name: '', party: '', election_id: '' })
      loadCandidates()
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to create candidate.' })
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this candidate?')) return
    try {
      await adminAPI.deleteCandidate(id)
      setMessage({ type: 'success', text: 'Candidate deleted successfully!' })
      loadCandidates()
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete candidate.' })
    }
  }

  if (loading) return <div className="loading-state">Loading candidates...</div>

  return (
    <div className="management-page">
      <div className="management-header">
        <h2>Candidates Management</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn btn-primary">
          <i className="fas fa-plus"></i> {showForm ? 'Cancel' : 'New Candidate'}
        </button>
      </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="card form-card">
          <h3>Add New Candidate</h3>
          <div className="form-group">
            <label className="label">Candidate ID</label>
            <input
              type="text"
              className="input"
              required
              placeholder="e.g., C001"
              value={formData.candidate_id}
              onChange={(e) => setFormData({ ...formData, candidate_id: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="label">Full Name</label>
            <input
              type="text"
              className="input"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="label">Party</label>
            <input
              type="text"
              className="input"
              placeholder="Optional"
              value={formData.party}
              onChange={(e) => setFormData({ ...formData, party: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="label">Election</label>
            {elections.length === 0 ? (
              <div className="input-error">
                <p style={{ color: '#ff6b6b', margin: '0.5rem 0', fontSize: '0.9rem' }}>
                  No elections available. Please create an election first.
                </p>
              </div>
            ) : (
              <select
                className="input"
                value={formData.election_id}
                onChange={(e) => setFormData({ ...formData, election_id: e.target.value })}
              >
                <option value="">Select an Election (optional - will use active election)</option>
                {elections.map((election) => (
                  <option key={election.id} value={election.id}>
                    {election.title} {election.is_active ? '(Active)' : ''}
                  </option>
                ))}
              </select>
            )}
          </div>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={elections.length === 0}
          >
            Create Candidate
          </button>
        </form>
      )}

      <div className="items-list">
        {candidates.length === 0 ? (
          <p className="empty-state">No candidates added yet.</p>
        ) : (
          candidates.map((candidate) => (
            <div key={candidate.candidate_id} className="item-card">
              <div className="item-content">
                <h3>{candidate.name}</h3>
                <p className="item-description">{candidate.party || 'Independent'}</p>
                <p className="item-id">ID: {candidate.candidate_id}</p>
              </div>
              <button
                onClick={() => handleDelete(candidate.candidate_id)}
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

export default CandidatesManagement

