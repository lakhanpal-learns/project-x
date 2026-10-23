import React, { useState, useEffect, useRef } from 'react';
import { AdminStats, ServiceRequest, CustomerWithHistory, ServicePackage } from '../types';

export const AdminDashboard: React.FC = () => {
  // State
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [customers, setCustomers] = useState<CustomerWithHistory[]>([]);
  const [services, setServices] = useState<ServicePackage[]>([]);
  
  // Navigation & Realtime
  const [activeTab, setActiveTab] = useState<'requests' | 'history' | 'customers' | 'services'>('requests');
  const [isLiveSync, setIsLiveSync] = useState<boolean>(true);
  
  // Filters & Pagination
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('active');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [timeSlot, setTimeSlot] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalCount, setTotalCount] = useState<number>(0);

  // Selected customer for full history drawer
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerWithHistory | null>(null);
  const [customerHistory, setCustomerHistory] = useState<ServiceRequest[]>([]);

  // Action modal
  const [selectedReq, setSelectedReq] = useState<ServiceRequest | null>(null);
  const [modalStatus, setModalStatus] = useState<string>('');
  const [modalDate, setModalDate] = useState<string>('');
  const [modalTime, setModalTime] = useState<string>('');
  const [modalNotes, setModalNotes] = useState<string>('');

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/v1/admin/stats');
      if (res.ok) setStats(await res.json());
    } catch {}
  };

  const fetchRequests = async () => {
    try {
      const q = new URLSearchParams({
        page: String(page),
        per_page: '10',
        ...(search ? { search } : {}),
        ...(statusFilter ? { status: statusFilter } : {}),
        ...(startDate ? { start_date: startDate } : {}),
        ...(endDate ? { end_date: endDate } : {}),
        ...(timeSlot ? { time_slot: timeSlot } : {}),
      });
      const res = await fetch(`/api/v1/admin/requests?${q.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setRequests(data.items || []);
        setTotalPages(data.total_pages || 1);
        setTotalCount(data.total || 0);
      }
    } catch {}
  };

  const fetchCustomers = async () => {
    try {
      const res = await fetch('/api/v1/admin/customers?page=1&per_page=20');
      if (res.ok) {
        const data = await res.json();
        setCustomers(data.items || []);
      }
    } catch {}
  };

  // Realtime Polling effect (10s)
  useEffect(() => {
    fetchStats();
    fetchRequests();
    fetchCustomers();

    if (!isLiveSync) return;
    const interval = setInterval(() => {
      fetchStats();
      if (activeTab === 'requests' || activeTab === 'history') fetchRequests();
      if (activeTab === 'customers') fetchCustomers();
    }, 10000);

    return () => clearInterval(interval);
  }, [isLiveSync, activeTab, page, search, statusFilter, startDate, endDate, timeSlot]);

  const updateRequestStage = async (id: number, newStage: string, notes?: string, date?: string, time?: string) => {
    try {
      const res = await fetch(`/api/v1/admin/requests/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStage,
          admin_notes: notes || null,
          scheduled_date: date || null,
          scheduled_time: time || null
        })
      });
      if (res.ok) {
        fetchRequests();
        fetchStats();
        setSelectedReq(null);
      }
    } catch {}
  };

  return (
    <div style={{ fontFamily: 'Poppins, sans-serif', background: '#f8fafc', minHeight: '100vh', padding: '24px' }}>
      {/* Header Bar */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, background: '#fff', padding: '16px 24px', borderRadius: 12, border: '1px solid #e2e8f0' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0, color: '#0f172a' }}>MrShine Operations Hub</h1>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Live Wash Bay Management &amp; Scheduling</span>
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <button 
            onClick={() => setIsLiveSync(!isLiveSync)} 
            style={{ 
              background: isLiveSync ? '#f0fdf4' : '#fef2f2', 
              color: isLiveSync ? '#166534' : '#991b1b', 
              border: `1px solid ${isLiveSync ? '#bbf7d0' : '#fecaca'}`,
              padding: '6px 14px', borderRadius: 20, fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' 
            }}
          >
            ● {isLiveSync ? 'Live Sync Active (10s)' : 'Sync Paused'}
          </button>
        </div>
      </header>

      {/* 7 Clean Side-by-side Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 12, marginBottom: 24 }}>
        {[
          { label: 'Total Bookings', val: stats?.total_requests ?? '-', color: '#0f172a' },
          { label: '1. Pending', val: stats?.pending_requests ?? '-', color: '#d97706' },
          { label: '2. Bay Scheduled', val: stats?.approved_requests ?? '-', color: '#2563eb' },
          { label: '3. In Bay Washing', val: stats?.in_progress_requests ?? '-', color: '#7c3aed' },
          { label: '4. Finished & Ready', val: stats?.completed_requests ?? '-', color: '#16a34a' },
          { label: '5. Declined', val: stats?.rejected_requests ?? '-', color: '#dc2626' },
          { label: 'Total Customers', val: stats?.total_customers ?? '-', color: '#0f172a' }
        ].map((c, i) => (
          <div key={i} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 10, padding: '14px', borderLeft: `4px solid ${c.color}` }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>{c.label}</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: c.color }}>{c.val}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, borderBottom: '2px solid #e2e8f0', marginBottom: 20 }}>
        <button 
          onClick={() => { setActiveTab('requests'); setStatusFilter('active'); }} 
          style={{ padding: '10px 18px', border: 'none', background: activeTab === 'requests' ? '#fff' : 'transparent', fontWeight: 600, borderTopLeftRadius: 8, borderTopRightRadius: 8, cursor: 'pointer' }}
        >
          🚗 Active Wash Queue ({totalCount})
        </button>
        <button 
          onClick={() => { setActiveTab('history'); setStatusFilter('history'); }} 
          style={{ padding: '10px 18px', border: 'none', background: activeTab === 'history' ? '#fff' : 'transparent', fontWeight: 600, borderTopLeftRadius: 8, borderTopRightRadius: 8, cursor: 'pointer' }}
        >
          📜 Order History &amp; Archive
        </button>
        <button 
          onClick={() => setActiveTab('customers')} 
          style={{ padding: '10px 18px', border: 'none', background: activeTab === 'customers' ? '#fff' : 'transparent', fontWeight: 600, borderTopLeftRadius: 8, borderTopRightRadius: 8, cursor: 'pointer' }}
        >
          👥 Customers Directory ({customers.length})
        </button>
      </div>

      {/* Tab Content: Service Orders with Side-by-side Filters */}
      {(activeTab === 'requests' || activeTab === 'history') && (
        <div style={{ background: '#fff', borderRadius: 12, border: '1px solid #e2e8f0', overflow: 'hidden' }}>
          {/* Side-by-side Filter Toolbar */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, padding: '16px 20px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
            <input 
              type="text" 
              placeholder="Search by ID, customer, vehicle..." 
              value={search} 
              onChange={(e) => setSearch(e.target.value)}
              style={{ flex: '1 1 220px', height: 38, padding: '0 12px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: '0.84rem' }}
            />
            <select 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)} 
              style={{ height: 38, padding: '0 10px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: '0.84rem' }}
            >
              <option value="">All Statuses</option>
              <option value="Pending">Pending Review</option>
              <option value="Approved">Bay Scheduled</option>
              <option value="In Progress">In Bay Washing</option>
              <option value="Completed">Completed</option>
              <option value="Rejected">Declined</option>
            </select>
            <input 
              type="date" 
              value={startDate} 
              onChange={(e) => setStartDate(e.target.value)} 
              style={{ height: 38, padding: '0 8px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: '0.82rem' }}
            />
            <input 
              type="date" 
              value={endDate} 
              onChange={(e) => setEndDate(e.target.value)} 
              style={{ height: 38, padding: '0 8px', borderRadius: 6, border: '1px solid #cbd5e1', fontSize: '0.82rem' }}
            />
            <button 
              onClick={() => { setSearch(''); setStatusFilter(''); setStartDate(''); setEndDate(''); }}
              style={{ height: 38, padding: '0 12px', background: '#e2e8f0', border: 'none', borderRadius: 6, fontWeight: 600, fontSize: '0.8rem', cursor: 'pointer' }}
            >
              Reset
            </button>
          </div>

          {/* Table */}
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontSize: '0.72rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '12px 18px', width: 90 }}>ID</th>
                  <th style={{ padding: '12px 18px' }}>Customer</th>
                  <th style={{ padding: '12px 18px' }}>Treatment</th>
                  <th style={{ padding: '12px 18px' }}>Vehicle</th>
                  <th style={{ padding: '12px 18px' }}>Scheduled</th>
                  <th style={{ padding: '12px 18px' }}>Stage</th>
                  <th style={{ padding: '12px 18px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((r) => (
                  <tr key={r.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '14px 18px', whiteSpace: 'nowrap' }}>
                      <strong style={{ fontSize: '0.92rem', color: '#0f172a' }}>#{r.id}</strong>
                      <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                        {new Date(r.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </div>
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <div style={{ fontWeight: 600, color: '#0f172a' }}>{r.customer_name}</div>
                      <div style={{ fontSize: '0.76rem', color: '#64748b' }}>{r.customer_email}</div>
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <div style={{ fontWeight: 600 }}>{r.service_name}</div>
                      <span style={{ fontSize: '0.74rem', color: '#059669', fontWeight: 600 }}>
                        {r.service_price ? `$${r.service_price}` : 'Custom Quote'}
                      </span>
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <div>{r.vehicle_details}</div>
                      {r.admin_notes && (
                        <div style={{ fontSize: '0.74rem', background: '#eff6ff', color: '#1e40af', padding: '2px 6px', borderRadius: 4, marginTop: 4 }}>
                          Note: {r.admin_notes}
                        </div>
                      )}
                    </td>
                    <td style={{ padding: '14px 18px', whiteSpace: 'nowrap' }}>
                      <div style={{ fontWeight: 600 }}>📅 {r.preferred_date}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>⏰ {r.preferred_time}</div>
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <span style={{ 
                        padding: '4px 10px', borderRadius: 16, fontSize: '0.74rem', fontWeight: 600,
                        background: r.status === 'Completed' ? '#dcfce7' : r.status === 'In Progress' ? '#ede9fe' : r.status === 'Approved' ? '#dbeafe' : '#fef3c7',
                        color: r.status === 'Completed' ? '#166534' : r.status === 'In Progress' ? '#5b21b6' : r.status === 'Approved' ? '#1e40af' : '#92400e'
                      }}>
                        ● {r.status}
                      </span>
                    </td>
                    <td style={{ padding: '14px 18px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                      {r.status === 'Pending' && (
                        <button 
                          onClick={() => updateRequestStage(r.id, 'Approved')} 
                          style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '5px 10px', borderRadius: 6, fontSize: '0.74rem', fontWeight: 600, cursor: 'pointer', marginRight: 6 }}
                        >
                          Schedule
                        </button>
                      )}
                      {r.status === 'Approved' && (
                        <button 
                          onClick={() => updateRequestStage(r.id, 'In Progress')} 
                          style={{ background: '#7c3aed', color: '#fff', border: 'none', padding: '5px 10px', borderRadius: 6, fontSize: '0.74rem', fontWeight: 600, cursor: 'pointer', marginRight: 6 }}
                        >
                          Start Wash
                        </button>
                      )}
                      {r.status === 'In Progress' && (
                        <button 
                          onClick={() => updateRequestStage(r.id, 'Completed')} 
                          style={{ background: '#10b981', color: '#fff', border: 'none', padding: '5px 10px', borderRadius: 6, fontSize: '0.74rem', fontWeight: 600, cursor: 'pointer', marginRight: 6 }}
                        >
                          ✓ Complete
                        </button>
                      )}
                      <button 
                        onClick={() => {
                          setSelectedReq(r);
                          setModalStatus(r.status);
                          setModalDate(r.preferred_date);
                          setModalTime(r.preferred_time);
                          setModalNotes(r.admin_notes || '');
                        }} 
                        style={{ background: '#f1f5f9', color: '#334155', border: '1px solid #cbd5e1', padding: '5px 8px', borderRadius: 6, fontSize: '0.74rem', cursor: 'pointer' }}
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 20px', borderTop: '1px solid #e2e8f0', fontSize: '0.82rem', color: '#64748b' }}>
            <span>Page {page} of {totalPages} (Total: {totalCount})</span>
            <div style={{ display: 'flex', gap: 6 }}>
              <button disabled={page <= 1} onClick={() => setPage(page - 1)} style={{ padding: '4px 10px', borderRadius: 4, border: '1px solid #cbd5e1', cursor: 'pointer' }}>Prev</button>
              <button disabled={page >= totalPages} onClick={() => setPage(page + 1)} style={{ padding: '4px 10px', borderRadius: 4, border: '1px solid #cbd5e1', cursor: 'pointer' }}>Next</button>
            </div>
          </div>
        </div>
      )}

      {/* Tab Content: Customer Directory with Booking History Drawer */}
      {activeTab === 'customers' && (
        <div style={{ background: '#fff', borderRadius: 12, border: '1px solid #e2e8f0', padding: 20 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ color: '#475569', fontSize: '0.72rem', textTransform: 'uppercase' }}>
                <th style={{ padding: 10 }}>Customer</th>
                <th style={{ padding: 10 }}>Contact</th>
                <th style={{ padding: 10 }}>Joined</th>
                <th style={{ padding: 10 }}>Lifetime Stats</th>
                <th style={{ padding: 10, textAlign: 'right' }}>History</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => (
                <tr key={c.id} style={{ borderTop: '1px solid #f1f5f9' }}>
                  <td style={{ padding: 12 }}>
                    <strong>{c.name}</strong>
                  </td>
                  <td style={{ padding: 12 }}>{c.email}</td>
                  <td style={{ padding: 12 }}>{new Date(c.created_at).toLocaleDateString()}</td>
                  <td style={{ padding: 12 }}>
                    <span style={{ background: '#eff6ff', color: '#1d4ed8', padding: '2px 8px', borderRadius: 10, fontSize: '0.75rem', fontWeight: 600 }}>
                      {c.summary.total_bookings} Bookings ({c.summary.completed} Done)
                    </span>
                  </td>
                  <td style={{ padding: 12, textAlign: 'right' }}>
                    <button 
                      onClick={async () => {
                        setSelectedCustomer(c);
                        const res = await fetch(`/api/v1/admin/requests?customer_id=${c.id}&per_page=50`);
                        if (res.ok) {
                          const data = await res.json();
                          setCustomerHistory(data.items || []);
                        }
                      }}
                      style={{ background: '#0f172a', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: 6, fontSize: '0.76rem', cursor: 'pointer' }}
                    >
                      View History
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal: Customer History Drawer */}
      {selectedCustomer && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#fff', borderRadius: 12, width: 680, maxHeight: '85vh', overflowY: 'auto', padding: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ margin: 0 }}>{selectedCustomer.name}'s Service History</h3>
              <button onClick={() => setSelectedCustomer(null)} style={{ border: 'none', background: 'none', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>
            </div>
            {customerHistory.map((h) => (
              <div key={h.id} style={{ background: '#f8fafc', padding: 12, borderRadius: 8, marginBottom: 8, border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                  <span>{h.service_name} (#{h.id})</span>
                  <span>{h.status}</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: 4 }}>
                  Vehicle: {h.vehicle_details} | Scheduled: {h.preferred_date} ({h.preferred_time})
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
