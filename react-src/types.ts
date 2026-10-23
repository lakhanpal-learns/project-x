export interface ServiceRequest {
  id: number;
  customer_id: number;
  service_id: number | null;
  custom_service: string | null;
  vehicle_details: string;
  preferred_date: string;
  preferred_time: string;
  message: string | null;
  admin_notes: string | null;
  status: 'Pending' | 'Approved' | 'In Progress' | 'Completed' | 'Rejected';
  created_at: string;
  decided_at: string | null;
  customer_name: string;
  customer_email: string;
  customer_phone: string | null;
  service_name: string;
  service_price: number | null;
}

export interface CustomerSummary {
  total_bookings: number;
  completed: number;
  in_progress: number;
  pending: number;
  approved: number;
  rejected: number;
}

export interface CustomerWithHistory {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  summary: CustomerSummary;
  recent_requests: ServiceRequest[];
}

export interface ServicePackage {
  id: number;
  name: string;
  description: string | null;
  price: number;
  duration_minutes: number;
  image_url: string | null;
}

export interface AdminStats {
  total_requests: number;
  pending_requests: number;
  approved_requests: number;
  in_progress_requests: number;
  completed_requests: number;
  rejected_requests: number;
  total_customers: number;
}
