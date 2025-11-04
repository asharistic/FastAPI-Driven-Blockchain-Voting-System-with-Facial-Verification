import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import './DashboardOverview.css'

function DashboardOverview() {
  const [stats, setStats] = useState({
    total_votes: 0,
    total_voters: 0,
    total_candidates: 0,
    blockchain_blocks: 0,
    voters_who_voted: 0,
  })
  const [results, setResults] = useState({ results: [], total_votes: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, resultsRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getResults(),
      ])
      setStats(statsRes.data)
      setResults(resultsRes.data)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>
  }

  return (
    <div className="dashboard-overview">
      <h2 className="dashboard-title">Dashboard Overview</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-content">
            <div>
              <p className="stat-label">Total Votes</p>
              <p className="stat-value">{stats.total_votes || 0}</p>
            </div>
            <div className="stat-icon">
              <i className="fas fa-vote-yea"></i>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-content">
            <div>
              <p className="stat-label">Registered Voters</p>
              <p className="stat-value">{stats.total_voters || 0}</p>
            </div>
            <div className="stat-icon">
              <i className="fas fa-users"></i>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-content">
            <div>
              <p className="stat-label">Candidates</p>
              <p className="stat-value">{stats.total_candidates || 0}</p>
            </div>
            <div className="stat-icon">
              <i className="fas fa-user-tie"></i>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-content">
            <div>
              <p className="stat-label">Blockchain Blocks</p>
              <p className="stat-value">{stats.blockchain_blocks || 0}</p>
            </div>
            <div className="stat-icon">
              <i className="fas fa-cube"></i>
            </div>
          </div>
        </div>
      </div>

      <div className="results-summary">
        <h3>Voting Results Summary</h3>
        <div className="results-list">
          {results.results && results.results.length > 0 ? (
            results.results.map((result, index) => {
              const percentage = results.total_votes > 0 
                ? ((result.votes / results.total_votes) * 100).toFixed(1) 
                : 0
              return (
                <div key={result.candidate_id} className="result-item">
                  <div className="result-header">
                    <span className="result-rank">#{index + 1}</span>
                    <span className="result-name">{result.name}</span>
                    <span className="result-votes">{result.votes} votes</span>
                  </div>
                  <div className="result-bar">
                    <div 
                      className="result-bar-fill"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="result-percentage">{percentage}%</div>
                </div>
              )
            })
          ) : (
            <p className="no-results">No votes cast yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default DashboardOverview

