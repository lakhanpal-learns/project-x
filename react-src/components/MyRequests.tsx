import React, { useState, useEffect, useRef } from 'react';
import { ServiceRequest } from '../types';

export const MyRequests: React.FC = () => {
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  const fetchRequests = async (searchVal: string, statusVal: string, startVal: string, endVal: string) => {
    try {
      const params = new URLSearchParams();
      if (searchVal) params.set('search', searchVal);
      if (statusVal) params.set('status', statusVal);
      if (startVal) params.set('start_date', startVal);
      if (endVal) params.set('end_date', endVal);

      const token = localStorage.getItem('mrshine_access_token') || '';
      const res = await fetch(`/api/v1/requests/my?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error('Failed to load your requests');
      const data: ServiceRequest[] = await res.json();
      setRequests(data || []);
    } catch (err) {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests(search, status, startDate, endDate);
    const interval = setInterval(() => {
      fetchRequests(search, status, startDate, endDate);
    }, 10000); // 10s auto sync
    return () => clearInterval(interval);
  }, [status, startDate, endDate]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearch(val);
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(() => {
      fetchRequests(val, status, startDate, endDate);
    }, 250);
  };

  const handleReset = () => {
    setSearch('');
    setStatus('');
    setStartDate('');
    setEndDate('');
    fetchRequests('', '', '', '');
  };

  const getStageNumber = (st: string) => {
    if (st === 'Approved') return 2;
    if (st === 'In Progress') return 3;
    if (st === 'Completed') return 4;
    return 1;
  };

  return (
    <div style={{ maxWidth: 1140, margin: '0 auto', padding: '32px 16px', fontFamily: 'Poppins, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16, marginBottom: 24 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800, margin: 0, color: '#0f172a' }}>
              My Requests &amp; Live Tracking
            </h1>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '4px 12px', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 20, fontSize: '0.76rem', fontWeight: 700, color: '#1d4ed8' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#2563eb' }} />
              Live Sync
            </span>
          </div>
          <p style={{ margin: 0, color: '#64748b', fontSize: '0.88rem' }}>
            Track your appointment progress from bay reservation to quality finished shine.
          </p>
        </div>
        <a
          href="/request-service"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            padding: '10px 18px',
            background: '#0f172a',
            color: '#fff',
            borderRadius: 8,
            fontWeight: 700,
            fontSize: '0.88rem',
            textDecoration: 'none',
          }}
        >
          + Book Another Service
        </a>
      </div>

      {/* Filter Bar with Debounced Search */}
      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 14, marginBottom: 24, display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Search by vehicle, service, or #ID..."
          value={search}
          onChange={handleSearchChange}
          style={{ flex: '1 1 240px', height: 38, padding: '0 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.84rem' }}
        />
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          style={{ height: 38, padding: '0 10px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.82rem', background: '#fff' }}
        >
          <option value="">All Statuses</option>
          <option value="Pending">1. Pending Review</option>
          <option value="Approved">2. Bay Reserved</option>
          <option value="In Progress">3. Washing In Progress</option>
          <option value="Completed">4. Quality Finished</option>
          <option value="Rejected">5. Declined</option>
        </select>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.82rem', color: '#64748b' }}>
          <span>From</span>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            style={{ height: 38, padding: '0 8px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.82rem' }}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.82rem', color: '#64748b' }}>
          <span>To</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            style={{ height: 38, padding: '0 8px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.82rem' }}
          />
        </div>
        <button
          onClick={handleReset}
          style={{ height: 38, padding: '0 12px', background: 'transparent', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.82rem', fontWeight: 600, color: '#64748b', cursor: 'pointer' }}
        >
          ✕ Reset
        </button>
      </div>

      {/* Loading Skeletons */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[1, 2].map((n) => (
            <div
              key={n}
              style={{
                height: 180,
                borderRadius: 12,
                background: 'linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%)',
                backgroundSize: '200% 100%',
                animation: 'shimmerAnim 1.5s infinite',
              }}
            />
          ))}
        </div>
      ) : requests.length === 0 ? (
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 60, textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, margin: '0 0 6px', color: '#0f172a' }}>No Requests Found</h2>
          <p style={{ color: '#64748b', fontSize: '0.88rem', margin: '0 0 16px' }}>
            You haven't scheduled any detailing appointments yet, or no bookings match your filters.
          </p>
          <a
            href="/request-service"
            style={{ display: 'inline-block', padding: '10px 20px', background: '#0f172a', color: '#fff', borderRadius: 8, fontWeight: 700, fontSize: '0.88rem', textDecoration: 'none' }}
          >
            Book a Car Wash Package →
          </a>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {requests.map((r) => {
            const stage = getStageNumber(r.status);
            const isRejected = r.status === 'Rejected';

            return (
              <div
                key={r.id}
                style={{
                  background: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: 14,
                  padding: 24,
                  boxShadow: '0 2px 10px rgba(0,0,0,0.02)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
                  <div>
                    <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#64748b', letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 4 }}>
                      Request #{r.id} • Booked {new Date(r.created_at).toLocaleDateString()}
                    </div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: '0 0 6px', color: '#0f172a' }}>
                      {r.service_name}
                    </h3>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, fontSize: '0.84rem', color: '#475569' }}>
                      <span>Vehicle: <strong>{r.vehicle_details}</strong></span>
                      <span>Scheduled: <strong>📅 {r.preferred_date}</strong></span>
                      <span>Slot: <strong>⏰ {r.preferred_time}</strong></span>
                      <span>Price: <strong>{r.service_price ? `$${Number(r.service_price).toFixed(2)}` : 'Custom Quote'}</strong></span>
                    </div>
                  </div>
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 6,
                      padding: '4px 12px',
                      borderRadius: 20,
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      background:
                        r.status === 'Completed'
                          ? '#dcfce7'
                          : r.status === 'In Progress'
                          ? '#ede9fe'
                          : r.status === 'Approved'
                          ? '#dbeafe'
                          : r.status === 'Rejected'
                          ? '#fee2e2'
                          : '#fef3c7',
                      color:
                        r.status === 'Completed'
                          ? '#166534'
                          : r.status === 'In Progress'
                          ? '#5b21b6'
                          : r.status === 'Approved'
                          ? '#1e40af'
                          : r.status === 'Rejected'
                          ? '#991b1b'
                          : '#92400e',
                    }}
                  >
                    {r.status}
                  </span>
                </div>

                {isRejected ? (
                  <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: 14, color: '#991b1b', fontSize: '0.86rem', marginTop: 12 }}>
                    ⚠️ <strong>Appointment Declined:</strong> Our bays were fully booked during this slot. Please choose an alternative date.
                  </div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginTop: 22, paddingTop: 18, borderTop: '1px solid #f1f5f9', position: 'relative' }}>
                    {[
                      { num: 1, label: '1. Request Received', sub: 'Review pending' },
                      { num: 2, label: '2. Bay Reserved', sub: 'Date confirmed' },
                      { num: 3, label: '3. In Bay / Washing', sub: 'Detailing underway' },
                      { num: 4, label: '4. Quality Finished', sub: 'Ready for pickup' },
                    ].map((step) => {
                      const isCompleted = stage > step.num;
                      const isActive = stage === step.num;
                      return (
                        <div key={step.num} style={{ textAlign: 'center' }}>
                          <div
                            style={{
                              width: 34,
                              height: 34,
                              borderRadius: '50%',
                              margin: '0 auto 8px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontWeight: 800,
                              fontSize: '0.86rem',
                              background: isCompleted ? '#10b981' : isActive ? '#2563eb' : '#fff',
                              borderColor: isCompleted ? '#10b981' : isActive ? '#2563eb' : '#cbd5e1',
                              border: '2px solid',
                              color: isCompleted || isActive ? '#fff' : '#64748b',
                            }}
                          >
                            {isCompleted ? '✓' : step.num}
                          </div>
                          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: isActive ? '#1d4ed8' : isCompleted ? '#047857' : '#64748b' }}>
                            {step.label}
                          </div>
                          <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: 2 }}>{step.sub}</div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {r.admin_notes && (
                  <div style={{ marginTop: 14, padding: '10px 14px', background: '#eff6ff', borderLeft: '4px solid #3b82f6', borderRadius: 6, fontSize: '0.82rem', color: '#1e40af' }}>
                    <strong>Admin Note:</strong> {r.admin_notes}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
