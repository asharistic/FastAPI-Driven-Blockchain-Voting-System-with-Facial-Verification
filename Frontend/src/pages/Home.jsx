import { Link } from 'react-router-dom'
import { FileText, Shield, Link2 } from 'lucide-react'
import './Home.css'

function Home() {
  return (
    <div className="home-page">
      <div className="animated-background"></div>
      
      <div className="container">
        <div className="welcome-section">
          <h2>Welcome to the Future of Voting</h2>
          <p className="intro-text">
            Experience secure, transparent voting powered by blockchain technology and advanced facial verification. 
            Every vote is immutable, verifiable, and protected by cutting-edge security measures.
          </p>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <FileText className="feature-icon" size={64} strokeWidth={1.5} />
              </div>
              <h3>Easy Registration</h3>
              <p>Register as a voter with your unique ID and facial biometric data. Quick and secure registration process that takes just minutes.</p>
              <Link to="/register" className="btn btn-primary">Register Now →</Link>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <Shield className="feature-icon" size={64} strokeWidth={1.5} />
              </div>
              <h3>Secure Voting</h3>
              <p>Verify your identity using advanced facial recognition before casting your vote. Your privacy and security are our top priority.</p>
              <Link to="/vote" className="btn btn-primary">Cast Vote →</Link>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon-wrapper">
                <Link2 className="feature-icon" size={64} strokeWidth={1.5} />
              </div>
              <h3>Blockchain Technology</h3>
              <p>Every vote is stored in an immutable blockchain ledger, ensuring transparency and preventing any form of tampering or fraud.</p>
              <Link to="/admin/login" className="btn btn-primary">View Dashboard →</Link>
            </div>
          </div>

          <div className="info-section">
            <h3>How It Works</h3>
            <ol>
              <li><strong>Register:</strong> Capture your photo and register with a unique voter ID. Our system securely stores your facial biometric data using advanced encryption.</li>
              <li><strong>Verify:</strong> Before voting, verify your identity using facial recognition. This ensures only registered voters can cast votes and prevents duplicate voting.</li>
              <li><strong>Vote:</strong> Cast your vote for your preferred candidate. The process is simple, secure, and takes just seconds to complete.</li>
              <li><strong>Blockchain:</strong> Your vote is immediately stored in an immutable blockchain, ensuring it cannot be altered or deleted, providing complete transparency.</li>
            </ol>
          </div>

          <div className="info-section benefits-section">
            <h3>Why Choose Our System?</h3>
            <ul>
              <li>
                <span className="checkmark">✓</span>
                <div>
                  <strong>Transparency:</strong> 
                  <span> All votes are publicly verifiable on the blockchain</span>
                </div>
              </li>
              <li>
                <span className="checkmark">✓</span>
                <div>
                  <strong>Security:</strong> 
                  <span> Facial verification prevents fraudulent voting</span>
                </div>
              </li>
              <li>
                <span className="checkmark">✓</span>
                <div>
                  <strong>Immutability:</strong> 
                  <span> Once recorded, votes cannot be changed</span>
                </div>
              </li>
              <li>
                <span className="checkmark">✓</span>
                <div>
                  <strong>Privacy:</strong> 
                  <span> Your personal data is protected and encrypted</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
