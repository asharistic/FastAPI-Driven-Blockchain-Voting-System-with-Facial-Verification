import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import './Management.css'

function VotersManagement() {
  const [voters, setVoters] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    loadVoters()
  }, [])

  const loadVoters = async () => {
    try {
      const response = await adminAPI.getVoters()
      setVoters(response.data.voters || [])
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load voters.' })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this voter?')) return
    try {
      await adminAPI.deleteVoter(id)
      setMessage({ type: 'success', text: 'Voter deleted successfully!' })
      loadVoters()
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete voter.' })
    }
  }

  if (loading) return <div className="loading-state">Loading voters...</div>

  return (
    <div className="management-page">
      <div className="management-header">
        <h2>Voters Management</h2>
      </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="table-container card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Voter ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Face Data</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {voters.length === 0 ? (
              <tr>
                <td colSpan="5" className="empty-state">No voters registered yet.</td>
              </tr>
            ) : (
              voters.map((voter) => (
                <tr key={voter.voter_id}>
                  <td>{voter.voter_id}</td>
                  <td>{voter.name}</td>
                  <td>
                    <span className={`status-badge ${voter.has_voted ? 'voted' : 'not-voted'}`}>
                      {voter.has_voted ? '✓ Voted' : '⏳ Not Voted'}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${voter.has_face_data ? 'yes' : 'no'}`}>
                      {voter.has_face_data ? '✓ Yes' : '✗ No'}
                    </span>
                  </td>
                  <td>
                    <button
                      onClick={() => handleDelete(voter.voter_id)}
                      className="btn-delete"
                    >
                      <i className="fas fa-trash"></i> Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default VotersManagement

