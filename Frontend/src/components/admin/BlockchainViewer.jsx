import { useState, useEffect } from 'react'
import { adminAPI } from '../../services/api'
import './BlockchainViewer.css'

function BlockchainViewer() {
  const [blockchain, setBlockchain] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBlockchain()
  }, [])

  const loadBlockchain = async () => {
    try {
      const response = await adminAPI.getBlockchain()
      setBlockchain(response.data)
    } catch (error) {
      console.error('Failed to load blockchain:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading-state">Loading blockchain...</div>
  if (!blockchain) return <div className="loading-state">No blockchain data available.</div>

  return (
    <div className="blockchain-viewer">
      <h2>Blockchain Ledger</h2>
      
      <div className="blockchain-status card">
        <div className="status-item">
          <span className="status-label">Status:</span>
          <span className={`status-value ${blockchain.is_valid ? 'valid' : 'invalid'}`}>
            {blockchain.is_valid ? '✓ Valid' : '✗ Invalid'}
          </span>
        </div>
        <div className="status-item">
          <span className="status-label">Total Blocks:</span>
          <span className="status-value">{blockchain.length || 0}</span>
        </div>
      </div>

      <div className="blocks-list">
        {blockchain.chain && blockchain.chain.length > 0 ? (
          [...blockchain.chain].reverse().map((block, index) => (
            <div key={block.index} className="block-card card">
              <div className="block-header">
                <h3>Block #{block.index}</h3>
                <span className="block-time">
                  {new Date(block.timestamp).toLocaleString()}
                </span>
              </div>
              <div className="block-data-section">
                <p className="data-label">Data:</p>
                <pre className="block-data">
                  {JSON.stringify(block.data, null, 2)}
                </pre>
              </div>
              <div className="block-hashes">
                <div className="hash-item">
                  <span className="hash-label">Hash:</span>
                  <code className="hash-value">{block.hash}</code>
                </div>
                <div className="hash-item">
                  <span className="hash-label">Previous Hash:</span>
                  <code className="hash-value previous">{block.previous_hash}</code>
                </div>
              </div>
            </div>
          ))
        ) : (
          <p className="empty-state">No blocks in the blockchain yet.</p>
        )}
      </div>
    </div>
  )
}

export default BlockchainViewer

