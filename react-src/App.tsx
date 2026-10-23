import React, { useState, useEffect } from 'react';
import { AdminDashboard } from './components/AdminDashboard';
import { BookingForm } from './components/BookingForm';
import { MyRequests } from './components/MyRequests';

export const App: React.FC = () => {
  const [currentPath, setCurrentPath] = useState<string>(window.location.pathname);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string, e?: React.MouseEvent) => {
    if (e) e.preventDefault();
    window.history.pushState({}, '', path);
    setCurrentPath(path);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', fontFamily: 'Poppins, sans-serif' }}>
      {/* Navigation Header */}
      <header style={{ background: '#ffffff', borderBottom: '1px solid #e2e8f0', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 20px', height: 70, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <a href="/" onClick={(e) => navigate('/', e)} style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none', color: '#0f172a' }}>
            <span style={{ fontWeight: 800, fontSize: '1.25rem', letterSpacing: '-0.02em' }}>MrShine</span>
            <span style={{ fontSize: '0.65rem', fontWeight: 700, letterSpacing: '0.1em', background: '#f1f5f9', padding: '2px 8px', borderRadius: 4 }}>CAR WASH</span>
          </a>

          <nav style={{ display: 'flex', alignItems: 'center', gap: 20, fontSize: '0.88rem', fontWeight: 600 }}>
            <a href="/" onClick={(e) => navigate('/', e)} style={{ color: currentPath === '/' ? '#0f172a' : '#64748b', textDecoration: 'none' }}>Home</a>
            <a href="/services" onClick={(e) => navigate('/services', e)} style={{ color: currentPath === '/services' ? '#0f172a' : '#64748b', textDecoration: 'none' }}>Services</a>
            <a href="/request-service" onClick={(e) => navigate('/request-service', e)} style={{ color: currentPath === '/request-service' ? '#0f172a' : '#64748b', textDecoration: 'none' }}>Book Service</a>
            <a href="/my-requests" onClick={(e) => navigate('/my-requests', e)} style={{ color: currentPath === '/my-requests' ? '#0f172a' : '#64748b', textDecoration: 'none' }}>My Requests</a>
            <a href="/admin" onClick={(e) => navigate('/admin', e)} style={{ color: currentPath === '/admin' ? '#0f172a' : '#64748b', textDecoration: 'none' }}>Admin Hub</a>
          </nav>
        </div>
      </header>

      {/* Main Content View */}
      <main style={{ flex: 1 }}>
        {currentPath === '/admin' && <AdminDashboard />}
        {currentPath === '/request-service' && <BookingForm />}
        {currentPath === '/my-requests' && <MyRequests />}
        {(currentPath === '/' || currentPath === '/services') && (
          <div style={{ maxWidth: 1140, margin: '0 auto', padding: '60px 20px', textAlign: 'center' }}>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: '#0f172a', marginBottom: 12 }}>
              Premium Automotive Detailing & Care
            </h1>
            <p style={{ color: '#64748b', fontSize: '1.05rem', maxWidth: 640, margin: '0 auto 28px' }}>
              Hand washes, steam sanitation, paint correction, and ceramic protection tailored for showroom gloss.
            </p>
            <div style={{ display: 'flex', gap: 14, justifyContent: 'center' }}>
              <button
                onClick={() => navigate('/request-service')}
                style={{ background: '#0f172a', color: '#fff', border: 'none', padding: '12px 24px', borderRadius: 8, fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer' }}
              >
                Book Multi-Service Appointment →
              </button>
              <button
                onClick={() => navigate('/my-requests')}
                style={{ background: 'transparent', color: '#0f172a', border: '1px solid #cbd5e1', padding: '12px 24px', borderRadius: 8, fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer' }}
              >
                Track Live Booking
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ background: '#ffffff', borderTop: '1px solid #e2e8f0', padding: '24px 20px', textAlign: 'center', fontSize: '0.82rem', color: '#64748b' }}>
        &copy; {new Date().getFullYear()} MrShine Car Wash & Detailing. All rights reserved.
      </footer>
    </div>
  );
};

export default App;
