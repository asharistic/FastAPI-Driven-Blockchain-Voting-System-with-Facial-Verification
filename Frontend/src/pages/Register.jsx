
import { useState, useRef, useEffect } from 'react'
import { Camera, CameraOff, RotateCcw, User } from 'lucide-react'
import { voterAPI } from '../services/api'
import './Register.css'

function Register() {
  const [formData, setFormData] = useState({
    voter_id: '',
    name: '',
  })
  const [video, setVideo] = useState(false)
  const [stream, setStream] = useState(null)
  const [capturedImage, setCapturedImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  
  const videoRef = useRef(null)
  const canvasRef = useRef(null)

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

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!capturedImage) {
      setMessage({ type: 'error', text: 'Please capture your photo first.' })
      return
    }

    setLoading(true)
    setMessage({ type: '', text: '' })

    try {
      const base64Image = capturedImage.split(',')[1] // Remove data:image/jpeg;base64, prefix
      
      await voterAPI.register({
        voter_id: formData.voter_id,
        name: formData.name,
        face_image: base64Image,
      })

      setMessage({ type: 'success', text: 'Registration successful! You can now vote.' })
      
      // Reset form
      setFormData({ voter_id: '', name: '' })
      setCapturedImage(null)
      stopCamera()
      
      setTimeout(() => {
        setMessage({ type: '', text: '' })
      }, 5000)
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Registration failed. Please try again.' 
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-page">
      <div className="animated-background"></div>
      <div className="container">
        <div className="form-section">
          <h2>Voter Registration</h2>
          <p>Register yourself to participate in the voting process. Please ensure good lighting and a clear view of your face for the best results.</p>

          <form onSubmit={handleSubmit} className="voter-form card">
            <div className="form-group">
              <label htmlFor="voterName" className="label">Full Name</label>
              <input
                type="text"
                id="voterName"
                className="input"
                required
                placeholder="Enter your full name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label htmlFor="voterId" className="label">Voter ID</label>
              <input
                type="text"
                id="voterId"
                className="input"
                required
                placeholder="Enter unique voter ID (e.g., V001)"
                value={formData.voter_id}
                onChange={(e) => setFormData({ ...formData, voter_id: e.target.value })}
              />
              <small style={{ color: 'var(--text-light)', fontSize: '0.875rem', display: 'block', marginTop: '0.5rem' }}>
                Choose a unique identifier for yourself
              </small>
            </div>

            <div className="form-group">
              <label className="label">Face Capture</label>
              <p style={{ color: 'var(--text-light)', fontSize: '0.95rem', marginBottom: '1rem' }}>
                Capture a clear photo of your face for identity verification. Make sure your face is well-lit and clearly visible.
              </p>
              <div className="camera-section">
                {!video && !capturedImage && (
                  <div className="camera-placeholder">
                    <User className="placeholder-icon" size={48} />
                    <p>Click "Start Camera" to begin</p>
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
              {loading ? <span className="loading"></span> : 'Register Now'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Register

