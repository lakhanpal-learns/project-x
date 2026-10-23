import React, { useState, useEffect } from 'react';
import { ServicePackage } from '../types';

export const BookingForm: React.FC = () => {
  const [services, setServices] = useState<ServicePackage[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [isCustom, setIsCustom] = useState<boolean>(false);
  const [customText, setCustomText] = useState<string>('');

  const [vehicleMakeModel, setVehicleMakeModel] = useState<string>('');
  const [vehicleYearPlate, setVehicleYearPlate] = useState<string>('');
  const [preferredDate, setPreferredDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [preferredTime, setPreferredTime] = useState<string>('');
  const [message, setMessage] = useState<string>('');

  const [submitting, setSubmitting] = useState<boolean>(false);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    fetch('/api/v1/services')
      .then((res) => res.json())
      .then((data: ServicePackage[]) => {
        setServices(data || []);
        if (data && data.length > 0) {
          setSelectedIds([data[0].id]);
        }
      })
      .catch(() => {
        // Fallback services
        setServices([
          { id: 1, name: 'Exterior Car Wash', price: 25.0, duration_minutes: 30, description: 'Foam wash, spot-free rinse, wheel cleaning', image_url: null },
          { id: 2, name: 'Interior Deep Clean', price: 45.0, duration_minutes: 45, description: 'Complete vacuuming, steam sanitizing, dash polish', image_url: null },
          { id: 3, name: 'Complete Wash & Interior', price: 65.0, duration_minutes: 75, description: 'Hand wash + comprehensive interior deep treatment', image_url: null },
          { id: 4, name: 'Showroom Detailing & Wax', price: 110.0, duration_minutes: 120, description: 'Clay bar polish, synthetic sealant & leather care', image_url: null }
        ]);
        setSelectedIds([1]);
      })
      .finally(() => setLoading(false));
  }, []);

  const toggleService = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const selectedServices = services.filter((s) => selectedIds.includes(s.id));
  const totalPrice = selectedServices.reduce((sum, s) => sum + Number(s.price), 0);
  const totalDuration = selectedServices.reduce((sum, s) => sum + s.duration_minutes, 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAlert(null);

    if (selectedIds.length === 0 && !isCustom) {
      setAlert({ type: 'error', message: 'Please select at least one service package.' });
      return;
    }

    if (isCustom && !customText.trim() && selectedIds.length === 0) {
      setAlert({ type: 'error', message: 'Please describe the custom service you require.' });
      return;
    }

    if (vehicleMakeModel.trim().length < 2) {
      setAlert({ type: 'error', message: 'Please enter your vehicle make and model.' });
      return;
    }

    if (!preferredTime) {
      setAlert({ type: 'error', message: 'Please select an appointment time window.' });
      return;
    }

    const vehicleDetails = vehicleYearPlate.trim()
      ? `${vehicleMakeModel.trim()} (${vehicleYearPlate.trim()})`
      : vehicleMakeModel.trim();

    let serviceId: number | null = null;
    let customService: string | null = null;

    if (selectedServices.length === 1 && !isCustom) {
      serviceId = selectedServices[0].id;
    } else if (selectedServices.length > 0 && !isCustom) {
      serviceId = selectedServices[0].id;
      const names = selectedServices.map((s) => s.name).join(' + ');
      customService = `Multi-Service (${selectedServices.length}): ${names} [Total: $${totalPrice.toFixed(2)}]`;
    } else if (isCustom && selectedServices.length > 0) {
      serviceId = selectedServices[0].id;
      const names = selectedServices.map((s) => s.name).join(' + ');
      customService = `Multi-Service: ${names} + Custom: ${customText.trim()}`;
    } else if (isCustom) {
      customService = customText.trim();
    }

    const payload = {
      service_id: serviceId,
      custom_service: customService,
      vehicle_details: vehicleDetails,
      preferred_date: preferredDate,
      preferred_time: preferredTime,
      message: message.trim() || null,
    };

    setSubmitting(true);
    try {
      const res = await fetch('/api/v1/requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('mrshine_access_token') || ''}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to submit service booking.');
      }

      const result = await res.json();
      setAlert({
        type: 'success',
        message: `Booking submitted successfully! Reference #${result.id} for ${result.service_name || 'service'}. Redirecting to live tracking...`,
      });

      setTimeout(() => {
        window.location.href = '/my-requests';
      }, 1500);
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'An error occurred while booking.' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 1140, margin: '0 auto', padding: '32px 16px', fontFamily: 'Poppins, sans-serif' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 6px', color: '#0f172a' }}>
          Multi-Service Appointment Booking
        </h1>
        <p style={{ color: '#64748b', fontSize: '0.92rem', margin: 0 }}>
          Select multiple car care packages or add custom detailing treatments for your vehicle.
        </p>
      </div>

      {alert && (
        <div
          style={{
            padding: '12px 18px',
            borderRadius: 8,
            marginBottom: 20,
            fontSize: '0.88rem',
            background: alert.type === 'success' ? '#f0fdf4' : '#fef2f2',
            color: alert.type === 'success' ? '#166534' : '#991b1b',
            border: `1px solid ${alert.type === 'success' ? '#bbf7d0' : '#fecaca'}`,
          }}
        >
          {alert.message}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 0.85fr', gap: 32, alignItems: 'start' }}>
        {/* Left Column: Multi-Service Select & Vehicle Form */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 14, padding: 24 }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 16px', color: '#0f172a' }}>
            1. Select Care Packages
          </h2>

          {loading ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14 }}>
              {[1, 2, 3, 4].map((n) => (
                <div
                  key={n}
                  style={{
                    height: 120,
                    borderRadius: 10,
                    background: 'linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%)',
                    backgroundSize: '200% 100%',
                    animation: 'shimmerAnim 1.5s infinite',
                  }}
                />
              ))}
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14 }}>
              {services.map((svc) => {
                const checked = selectedIds.includes(svc.id);
                return (
                  <div
                    key={svc.id}
                    onClick={() => toggleService(svc.id)}
                    style={{
                      border: checked ? '1.5px solid #0f172a' : '1.5px solid #e2e8f0',
                      background: checked ? '#f8fafc' : '#ffffff',
                      borderRadius: 12,
                      padding: 16,
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      boxShadow: checked ? '0 0 0 1px #0f172a' : 'none',
                    }}
                  >
                    <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleService(svc.id)}
                        onClick={(e) => e.stopPropagation()}
                        style={{ width: 18, height: 18, marginTop: 2, accentColor: '#0f172a' }}
                      />
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a' }}>{svc.name}</div>
                        <div style={{ fontSize: '0.76rem', color: '#64748b', margin: '4px 0 10px' }}>
                          {svc.description}
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.74rem', background: '#f1f5f9', padding: '2px 8px', borderRadius: 4, fontWeight: 600 }}>
                            ⏱ {svc.duration_minutes}m
                          </span>
                          <span style={{ fontWeight: 800, fontSize: '1.05rem', color: '#0f172a' }}>
                            ${Number(svc.price).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Custom Service Option */}
              <div
                style={{
                  gridColumn: '1 / -1',
                  border: isCustom ? '1.5px solid #0f172a' : '1.5px dashed #cbd5e1',
                  borderRadius: 12,
                  padding: 16,
                  background: isCustom ? '#ffffff' : '#fafbfc',
                }}
              >
                <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                  <input
                    type="checkbox"
                    checked={isCustom}
                    onChange={(e) => setIsCustom(e.target.checked)}
                    style={{ width: 18, height: 18, accentColor: '#0f172a' }}
                  />
                  <div>
                    <strong style={{ fontSize: '0.92rem' }}>✨ Custom Service / Special Treatment</strong>
                    <div style={{ fontSize: '0.76rem', color: '#64748b' }}>
                      Add paint correction, deep stain extraction, or bespoke vehicle care
                    </div>
                  </div>
                </div>
                {isCustom && (
                  <div style={{ marginTop: 12 }}>
                    <input
                      type="text"
                      placeholder="e.g. Paint Correction + Scratch Removal + Engine Bay Degrease"
                      value={customText}
                      onChange={(e) => setCustomText(e.target.value)}
                      style={{
                        width: '100%',
                        height: 40,
                        padding: '0 12px',
                        border: '1px solid #cbd5e1',
                        borderRadius: 8,
                        fontSize: '0.86rem',
                        fontFamily: 'Poppins, sans-serif',
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '28px 0 16px', paddingTop: 20, borderTop: '1px solid #e2e8f0', color: '#0f172a' }}>
            2. Vehicle & Schedule
          </h2>

          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: 6 }}>
                  Vehicle Make & Model *
                </label>
                <input
                  type="text"
                  placeholder="e.g. BMW 330i or Tesla Model Y"
                  value={vehicleMakeModel}
                  onChange={(e) => setVehicleMakeModel(e.target.value)}
                  required
                  style={{ width: '100%', height: 42, padding: '0 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.86rem' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: 6 }}>
                  Year & Color (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. 2024, Metallic Gray"
                  value={vehicleYearPlate}
                  onChange={(e) => setVehicleYearPlate(e.target.value)}
                  style={{ width: '100%', height: 42, padding: '0 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.86rem' }}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: 6 }}>
                  Preferred Date *
                </label>
                <input
                  type="date"
                  min={new Date().toISOString().split('T')[0]}
                  value={preferredDate}
                  onChange={(e) => setPreferredDate(e.target.value)}
                  required
                  style={{ width: '100%', height: 42, padding: '0 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.86rem' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: 6 }}>
                  Preferred Time Window *
                </label>
                <select
                  value={preferredTime}
                  onChange={(e) => setPreferredTime(e.target.value)}
                  required
                  style={{ width: '100%', height: 42, padding: '0 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.86rem', background: '#fff' }}
                >
                  <option value="" disabled>Select window</option>
                  <option value="08:30 AM - 09:30 AM">08:30 AM - 09:30 AM (Early)</option>
                  <option value="10:00 AM - 11:30 AM">10:00 AM - 11:30 AM (Morning)</option>
                  <option value="11:30 AM - 01:00 PM">11:30 AM - 01:00 PM (Midday)</option>
                  <option value="02:00 PM - 03:30 PM">02:00 PM - 03:30 PM (Afternoon)</option>
                  <option value="03:30 PM - 05:00 PM">03:30 PM - 05:00 PM (Late Day)</option>
                  <option value="05:00 PM - 06:30 PM">05:00 PM - 06:30 PM (Evening)</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: 6 }}>
                Special Notes or Requests (Optional)
              </label>
              <textarea
                placeholder="Specific stains, delicate leather, pet hair, or special instructions..."
                rows={3}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: '0.86rem', fontFamily: 'Poppins, sans-serif' }}
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              style={{
                width: '100%',
                height: 48,
                background: '#0f172a',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                fontWeight: 700,
                fontSize: '0.95rem',
                cursor: submitting ? 'wait' : 'pointer',
                transition: 'background 0.15s ease',
              }}
            >
              {submitting ? 'Submitting Service Request...' : 'Confirm Multi-Service Booking →'}
            </button>
          </form>
        </div>

        {/* Right Column: Live Booking Summary */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 14, padding: 24, position: 'sticky', top: 90 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid #f1f5f9' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#0f172a' }}>Booking Summary</h3>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, background: '#0f172a', color: '#fff', padding: '3px 10px', borderRadius: 20 }}>
              {selectedServices.length + (isCustom ? 1 : 0)} selected
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
            {selectedServices.map((s) => (
              <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', background: '#f8fafc', padding: '8px 12px', borderRadius: 8 }}>
                <span>{s.name}</span>
                <strong>${Number(s.price).toFixed(2)}</strong>
              </div>
            ))}
            {isCustom && (
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', background: '#eff6ff', padding: '8px 12px', borderRadius: 8, color: '#1d4ed8' }}>
                <span>✨ {customText.trim() || 'Custom Detailing'}</span>
                <strong>Quote on site</strong>
              </div>
            )}
            {selectedServices.length === 0 && !isCustom && (
              <div style={{ fontSize: '0.82rem', color: '#94a3b8', textAlign: 'center', padding: '12px 0' }}>
                No services selected.
              </div>
            )}
          </div>

          <div style={{ fontSize: '0.84rem', color: '#475569', display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span>Est. Duration:</span>
            <strong>{totalDuration} mins {isCustom ? '+ inspection' : ''}</strong>
          </div>
          <div style={{ fontSize: '0.84rem', color: '#475569', display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span>Appointment:</span>
            <span>{preferredDate} {preferredTime ? `(${preferredTime.split(' ')[0]})` : ''}</span>
          </div>
          <div style={{ fontSize: '0.84rem', color: '#475569', display: 'flex', justifyContent: 'space-between', marginBottom: 14 }}>
            <span>Vehicle:</span>
            <span>{vehicleMakeModel || '—'}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 14, borderTop: '2px solid #0f172a', fontWeight: 800, fontSize: '1.25rem', color: '#0f172a' }}>
            <span>Estimated Total:</span>
            <span>${totalPrice.toFixed(2)} {isCustom ? '+ Quote' : ''}</span>
          </div>

          <div style={{ marginTop: 20, paddingTop: 14, borderTop: '1px dashed #e2e8f0', fontSize: '0.78rem', color: '#64748b', lineHeight: 1.5 }}>
            ✓ <strong>No advance payment:</strong> Pay after inspection on arrival.<br />
            ✓ <strong>Live updates:</strong> Follow real-time stages in your tracker.
          </div>
        </div>
      </div>
    </div>
  );
};
