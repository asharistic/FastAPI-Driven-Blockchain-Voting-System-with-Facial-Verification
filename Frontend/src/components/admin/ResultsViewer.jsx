import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import './ResultsViewer.css'

function ResultsViewer() {
  const [results, setResults] = useState({ results: [], total_votes: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadResults()
    const interval = setInterval(loadResults, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const loadResults = async () => {
    try {
      const response = await adminAPI.getResults()
      setResults(response.data)
    } catch (error) {
      console.error('Failed to load results:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading-state">Loading results...</div>

  return (
    <div className="results-viewer">
      <h2>Voting Results</h2>
      
      <div className="results-summary card">
        <h3>Total Votes: {results.total_votes || 0}</h3>
      </div>

      <div className="results-table-container card">
        <table className="results-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Candidate</th>
              <th>Party</th>
              <th>Votes</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            {results.results && results.results.length > 0 ? (
              results.results.map((result, index) => {
                const percentage = results.total_votes > 0
                  ? ((result.votes / results.total_votes) * 100).toFixed(1)
                  : 0
                return (
                  <tr key={result.candidate_id}>
                    <td className="rank-cell">#{index + 1}</td>
                    <td className="name-cell">{result.name}</td>
                    <td className="party-cell">{result.party || 'Independent'}</td>
                    <td className="votes-cell">{result.votes}</td>
                    <td className="percentage-cell">
                      <div className="percentage-bar-container">
                        <div 
                          className="percentage-bar"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="percentage-text">{percentage}%</span>
                    </td>
                  </tr>
                )
              })
            ) : (
              <tr>
                <td colSpan="5" className="empty-state">No votes cast yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ResultsViewer

