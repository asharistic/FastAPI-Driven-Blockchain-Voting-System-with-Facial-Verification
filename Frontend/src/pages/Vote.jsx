
import { useState, useRef, useEffect } from 'react'
import { Camera, CameraOff, RotateCcw, User, Shield, Vote as VoteIcon } from 'lucide-react'
import { voterAPI, voteAPI } from '../services/api'
import './Vote.css'

function Vote() {
  const [step, setStep] = useState('verify') // 'verify' or 'vote'
  const [voterId, setVoterId] = useState('')
  const [voterName, setVoterName] = useState('')
  const [video, setVideo] = useState(null)
  const [stream, setStream] = useState(null)
  const [capturedImage, setCapturedImage] = useState(null)
  const [candidates, setCandidates] = useState([])
  const [selectedCandidate, setSelectedCandidate] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  
  const videoRef = useRef(null)
  const canvasRef = useRef(null)

  useEffect(() => {
    if (step === 'vote') {
      loadCandidates()
    }
  }, [step])

  // Handle video stream when it's set
  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream
      videoRef.current.play()
        .then(() => {
          console.log('Video started playing')
        })
        .catch(err => {
          console.error('Error playing video:', err)
          setMessage({ type: 'error', text: 'Failed to start video stream.' })
        })
    }
  }, [stream])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [stream])

  const loadCandidates = async () => {
    try {
      const response = await voteAPI.getCandidates()
      setCandidates(response.data.candidates || [])
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load candidates.' })
    }
  }

  const startCamera = async () => {
    try {
      // Stop any existing stream first
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        } 
      })
      setStream(mediaStream)
      setVideo(true)
    } catch (error) {
      console.error('Camera error:', error)
      setMessage({ type: 'error', text: 'Failed to access camera. Please allow camera permissions.' })
      setVideo(false)
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0)
      
      const imageData = canvas.toDataURL('image/jpeg')
      setCapturedImage(imageData)
      setVideo(false)
    }
  }

  const retakePhoto = () => {
    setCapturedImage(null)
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream
      setVideo(true)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setVideo(false)
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    
    if (!capturedImage) {
      setMessage({ type: 'error', text: 'Please capture your photo first.' })
      return
    }

    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const base64Image = capturedImage.split(',')[1]
      
      const response = await voterAPI.verifyFace({
        voter_id: voterId,
        face_image: base64Image,
      })

      // Backend returns 'voter_name' in the response
      setVoterName(response.data.voter_name || response.data.name || 'Voter')
      setStep('vote')
      setMessage({ type: 'success', text: 'Verification successful! You can now cast your vote.' })
      // Keep capturedImage for duplicate face check during voting
      stopCamera()
      
      setTimeout(() => {
        setMessage({ type: '', text: '' })
      }, 3000)
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Verification failed. Please try again.' 
      })
    } finally {
      setLoading(false)
    }
  }

  const handleVote = async () => {
    if (!selectedCandidate) {
      setMessage({ type: 'error', text: 'Please select a candidate.' })
      return
    }

    if (!capturedImage) {
      setMessage({ type: 'error', text: 'Face verification required. Please go back and verify your face again.' })
      return
    }

    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const base64Image = capturedImage.split(',')[1]
      
      await voteAPI.castVote({
        voter_id: voterId,
        candidate_id: selectedCandidate,
        face_image: base64Image,
      })

      setMessage({ type: 'success', text: 'Vote cast successfully! Thank you for voting.' })
      
      setTimeout(() => {
        setStep('verify')
        setVoterId('')
        setVoterName('')
        setSelectedCandidate('')
        setMessage({ type: '', text: '' })
      }, 3000)
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to cast vote. Please try again.' 
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="vote-page">
      <div className="animated-background"></div>
      <div className="container">
        <div className="form-section">
          {step === 'verify' ? (
            <>
              <div className="section-header">
                <Shield className="section-icon" size={48} />
                <h2>Face Verification</h2>
              </div>
              <p>Verify your identity before casting your vote. This ensures secure and legitimate voting.</p>

              <form onSubmit={handleVerify} className="voter-form card">
                <div className="form-group">
                  <label htmlFor="voterId" className="label">Voter ID</label>
                  <input
                    type="text"
                    id="voterId"
                    className="input"
                    required
                    placeholder="Enter your registered voter ID"
                    value={voterId}
                    onChange={(e) => setVoterId(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="label">Face Verification</label>
                  <p style={{ color: 'var(--text-light)', fontSize: '0.95rem', marginBottom: '1rem' }}>
                    Capture your photo to verify your identity. Ensure good lighting and a clear view of your face.
                  </p>
                  <div className="camera-section">
                    {!video && !capturedImage && (
                      <div className="camera-placeholder">
                        <User className="placeholder-icon" size={48} />
                        <p>Click "Start Camera" to begin verification</p>
                      </div>
                    )}
                    {video && (
                      <div className="video-container">
                        <video 
                          ref={videoRef} 
                          autoPlay 
                          playsInline 
                          muted
                          className="camera-video"
                        ></video>
                      </div>
                    )}
                    {capturedImage && (
                      <div className="captured-image">
                        <img src={capturedImage} alt="Captured" />
                      </div>
                    )}
                    <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
                  </div>
                  <div className="camera-controls">
                    {!video && !capturedImage && (
                      <button type="button" onClick={startCamera} className="btn btn-secondary">
                        <Camera size={18} style={{ marginRight: '0.5rem' }} />
                        Start Camera
                      </button>
                    )}
                    {video && (
                      <>
                        <button type="button" onClick={capturePhoto} className="btn btn-secondary">
                          <Camera size={18} style={{ marginRight: '0.5rem' }} />
                          Capture Photo
                        </button>
                        <button type="button" onClick={stopCamera} className="btn btn-secondary">
                          <CameraOff size={18} style={{ marginRight: '0.5rem' }} />
                          Stop Camera
                        </button>
                      </>
                    )}
                    {capturedImage && (
                      <button type="button" onClick={retakePhoto} className="btn btn-secondary">
                        <RotateCcw size={18} style={{ marginRight: '0.5rem' }} />
                        Retake Photo
                      </button>
                    )}
                  </div>
                </div>

                {message.text && (
                  <div className={`message ${message.type}`}>
                    {message.text}
                  </div>
                )}

                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  style={{ width: '100%', fontSize: '1.05rem', padding: '1rem' }}
                  disabled={loading}
                >
                  {loading ? <span className="loading"></span> : 'Verify Identity'}
                </button>
              </form>
            </>
          ) : (
            <>
              <div className="section-header">
                <VoteIcon className="section-icon" size={48} />
                <h2>Cast Your Vote</h2>
              </div>
              <p style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-light)', textAlign: 'center' }}>
                Welcome, <strong style={{ color: 'var(--gold)', fontSize: '1.15rem' }}>{voterName}</strong>!
              </p>
              
              {/* Display Election Information */}
              {candidates.length > 0 && (() => {
                // Get unique elections from candidates
                const uniqueElections = new Map()
                candidates.forEach(c => {
                  if (c.election_title && !uniqueElections.has(c.election_id)) {
                    uniqueElections.set(c.election_id, {
                      title: c.election_title,
                      description: c.election_description
                    })
                  }
                })
                
                // If all candidates are from the same election, show it once at the top
                if (uniqueElections.size === 1) {
                  const election = Array.from(uniqueElections.values())[0]
                  return (
                    <div style={{ 
                      background: 'rgba(212, 175, 55, 0.1)', 
                      border: '2px solid var(--border-gold)', 
                      borderRadius: '12px', 
                      padding: '1.5rem', 
                      marginBottom: '2rem',
                      textAlign: 'center'
                    }}>
                      <h3 style={{ color: 'var(--gold)', marginBottom: '0.5rem', fontSize: '1.3rem' }}>
                        {election.title}
                      </h3>
                      {election.description && (
                        <p style={{ color: 'var(--text-light)', fontSize: '0.95rem', margin: 0 }}>
                          {election.description}
                        </p>
                      )}
                    </div>
                  )
                }
                return null
              })()}
              
              <p style={{ fontSize: '1.05rem', marginBottom: '2rem', color: 'var(--text-light)', textAlign: 'center' }}>
                Please select your preferred candidate:
              </p>

              <div className="candidates-list">
                {candidates.map((candidate) => (
                  <div
                    key={candidate.candidate_id}
                    className={`candidate-card ${selectedCandidate === candidate.candidate_id ? 'selected' : ''}`}
                    onClick={() => setSelectedCandidate(candidate.candidate_id)}
                  >
                    <div className="candidate-info">
                      <h4>{candidate.name}</h4>
                      <p>{candidate.party || 'Independent'}</p>
                      <p className="candidate-id">ID: {candidate.candidate_id}</p>
                      {candidate.election_title && (() => {
                        // Show election title on card if there are multiple different elections
                        const uniqueElections = new Set(candidates.map(c => c.election_id).filter(Boolean))
                        if (uniqueElections.size > 1) {
                          return (
                            <p style={{ 
                              fontSize: '0.85rem', 
                              color: 'var(--gold)', 
                              marginTop: '0.5rem',
                              opacity: 0.8 
                            }}>
                              {candidate.election_title}
                            </p>
                          )
                        }
                        return null
                      })()}
                    </div>
                    {selectedCandidate === candidate.candidate_id && (
                      <div className="selected-indicator">✓</div>
                    )}
                  </div>
                ))}
              </div>

              {message.text && (
                <div className={`message ${message.type}`} style={{ marginTop: '2rem' }}>
                  {message.text}
                </div>
              )}

              <button
                onClick={handleVote}
                className="btn btn-primary"
                style={{ width: '100%', fontSize: '1.05rem', padding: '1rem', marginTop: '2rem' }}
                disabled={loading || !selectedCandidate}
              >
                {loading ? <span className="loading"></span> : 'Cast Vote'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Vote

