import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminAPI } from '../../services/api'
import DashboardOverview from '../../components/admin/DashboardOverview'
import ElectionsManagement from '../../components/admin/ElectionsManagement'
import CandidatesManagement from '../../components/admin/CandidatesManagement'
import VotersManagement from '../../components/admin/VotersManagement'
import BlockchainViewer from '../../components/admin/BlockchainViewer'
import ResultsViewer from '../../components/admin/ResultsViewer'
import './AdminDashboard.css'

function AdminDashboard() {
  const [activeSection, setActiveSection] = useState('dashboard')
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    navigate('/admin/login')
  }

  return (
    <div className="admin-dashboard">
      <nav className="admin-nav">
        <div className="admin-nav-content">
          <div className="admin-nav-left">
            <button id="sidebarToggle" className="sidebar-toggle">
              <i className="fas fa-bars"></i>
            </button>
            <h1 className="admin-title">🗳️ Blockchain Voting Admin</h1>
          </div>
          <div className="admin-nav-right">
            <div className="admin-user">
              <i className="fas fa-user-shield"></i>
              <span>Admin</span>
            </div>
            <button onClick={handleLogout} className="btn-logout">
              <i className="fas fa-sign-out-alt"></i> Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="admin-content-wrapper">
        <aside id="sidebar" className="admin-sidebar">
          <nav className="sidebar-nav">
            <a
              href="#dashboard"
              onClick={(e) => { e.preventDefault(); setActiveSection('dashboard') }}
              className={`sidebar-link ${activeSection === 'dashboard' ? 'active' : ''}`}
            >
              <i className="fas fa-chart-line"></i>
              <span>Dashboard</span>
            </a>
            <a
              href="#elections"
              onClick={(e) => { e.preventDefault(); setActiveSection('elections') }}
              className={`sidebar-link ${activeSection === 'elections' ? 'active' : ''}`}
            >
              <i className="fas fa-calendar-check"></i>
              <span>Elections</span>
            </a>
            <a
              href="#candidates"
              onClick={(e) => { e.preventDefault(); setActiveSection('candidates') }}
              className={`sidebar-link ${activeSection === 'candidates' ? 'active' : ''}`}
            >
              <i className="fas fa-users"></i>
              <span>Candidates</span>
            </a>
            <a
              href="#voters"
              onClick={(e) => { e.preventDefault(); setActiveSection('voters') }}
              className={`sidebar-link ${activeSection === 'voters' ? 'active' : ''}`}
            >
              <i className="fas fa-user-check"></i>
              <span>Voters</span>
            </a>
            <a
              href="#blockchain"
              onClick={(e) => { e.preventDefault(); setActiveSection('blockchain') }}
              className={`sidebar-link ${activeSection === 'blockchain' ? 'active' : ''}`}
            >
              <i className="fas fa-cubes"></i>
              <span>Blockchain</span>
            </a>
            <a
              href="#results"
              onClick={(e) => { e.preventDefault(); setActiveSection('results') }}
              className={`sidebar-link ${activeSection === 'results' ? 'active' : ''}`}
            >
              <i className="fas fa-poll"></i>
              <span>Results</span>
            </a>
          </nav>
        </aside>

        <main className="admin-main">
          {activeSection === 'dashboard' && <DashboardOverview />}
          {activeSection === 'elections' && <ElectionsManagement />}
          {activeSection === 'candidates' && <CandidatesManagement />}
          {activeSection === 'voters' && <VotersManagement />}
          {activeSection === 'blockchain' && <BlockchainViewer />}
          {activeSection === 'results' && <ResultsViewer />}
        </main>
      </div>
    </div>
  )
}

export default AdminDashboard

