import { Outlet, Link, useLocation } from 'react-router-dom'
import './Layout.css'

function Layout() {
  const location = useLocation()

  return (
    <div className="layout">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <h1 className="logo">🗳️ Blockchain Voting System</h1>
            <p className="subtitle">Secure, Transparent, and Immutable Voting Platform</p>
          </div>
        </div>
      </header>

      {!location.pathname.startsWith('/admin') && (
        <nav className="nav-menu">
          <div className="container">
            <Link 
              to="/" 
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              Home
            </Link>
            <Link 
              to="/register" 
              className={`nav-link ${location.pathname === '/register' ? 'active' : ''}`}
            >
              Register
            </Link>
            <Link 
              to="/vote" 
              className={`nav-link ${location.pathname === '/vote' ? 'active' : ''}`}
            >
              Vote
            </Link>
            <Link 
              to="/admin/login" 
              className={`nav-link ${location.pathname === '/admin/login' ? 'active' : ''}`}
            >
              Admin
            </Link>
          </div>
        </nav>
      )}

      <main className="main-content">
        <Outlet />
      </main>

      <footer className="footer">
        <div className="container">
          <p>Blockchain Voting System &copy; 2025 | Final Year Project</p>
        </div>
      </footer>
    </div>
  )
}

export default Layout

