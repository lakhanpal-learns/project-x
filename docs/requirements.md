# Project Requirements — MrShine Car Wash Website

## 1. Project Overview

Build a simple, functional customer request management system for the existing MrShine Car Wash website.

Customers must be able to register, log in, submit service requests, and view their request history. The admin must be able to view incoming requests, approve or reject them, and see basic request statistics.

When the admin makes a decision, the customer should receive an email and WhatsApp notification.

The goal is to build a working system with the minimum features required by the client.

## 2. Technology Stack

- **Frontend:** Existing HTML, CSS, and minimal JavaScript
- **Backend:** Python with FastAPI
- **Database:** PostgreSQL
- **Database ORM:** SQLAlchemy
- **Deployment:** Render
- **Notifications:** Email service and WhatsApp Business Platform

## 3. Customer Features

### Registration and Login

Customers should be able to:
- Register using their name, email, phone number, and password.
- Log in and log out.
- Access the request form only after logging in.

Passwords must be stored securely as hashes.

### Submit a Request

After logging in, customers can submit a service request with:

- Selected car wash service
- Vehicle details
- Preferred date and time
- Optional message

The system should save each request with a default status of `Pending`.

### Customer Dashboard

Customers should be able to:
- View their submitted requests.
- See the status of each request: Pending, Approved, or Rejected.
- View basic request details and submission dates.

Customers must only be able to view their own requests.

## 4. Admin Features

### Admin Login

Provide a protected admin login. Initially, one administrator account is sufficient.

### Admin Dashboard

Display these statistics:

- Total requests
- Pending requests
- Approved requests
- Rejected requests

The numbers must come from the database.

### Manage Requests

The admin should be able to:

- View all customer requests.
- See the customer's name, email, phone number, requested service, and preferred date/time.
- View request details.
- Approve a pending request.
- Reject a pending request.

When a decision is made, the request status must be updated in the database.

## 5. Email and WhatsApp Notifications

After the admin approves or rejects a request:

- Send an email to the customer.
- Send a WhatsApp message to the customer's registered phone number.
- Include the requested service and decision in the notification.

Use a configured email provider and WhatsApp Business provider.

Save the request decision before sending notifications so that a notification failure does not lose the decision.

## 6. Database Tables

Keep the database simple. Start with three tables.

### `users`

Stores customer and admin accounts.

Fields:
- `id`
- `name`
- `email`
- `phone`
- `password_hash`
- `role` — customer or admin
- `created_at`

### `services`

Stores the services offered by the business.

Fields:
- `id`
- `name`
- `description`
- `price`

### `requests`

Stores customer service requests.

Fields:
- `id`
- `customer_id`
- `service_id`
- `vehicle_details`
- `preferred_date`
- `preferred_time`
- `message`
- `status`
- `created_at`
- `decided_at`

The `customer_id` links a request to its customer, and `service_id` links a request to the selected service.

Notification tracking can be kept simple initially and added to the database if needed.

## 7. Website Pages

### Public Website
- Home
- Services and pricing
- Contact information
- Register
- Login

### Customer Area
- Submit request
- My dashboard
- My request history

### Admin Area
- Admin login
- Dashboard overview
- All requests
- Request details
- Approve and reject actions

Keep the existing website design wherever possible. Add only the JavaScript needed to connect the frontend to the Python backend.

## 8. Basic Security Requirements

- Hash passwords securely.
- Require login before request submission.
- Protect admin pages and API endpoints.
- Allow customers to access only their own requests.
- Allow only admins to approve or reject requests.
- Keep database credentials and API keys in environment variables.

## 9. Development Plan

### Phase 1 — Setup
- Review the existing website.
- Create the FastAPI backend.
- Connect PostgreSQL.
- Create the database tables.

### Phase 2 — Authentication
- Implement customer registration and login.
- Create the initial admin account.
- Protect customer and admin routes.

### Phase 3 — Customer Requests
- Display available services.
- Build the request form.
- Save requests in PostgreSQL.
- Build the customer dashboard and request history.

### Phase 4 — Admin Dashboard
- Display total, pending, approved, and rejected requests.
- Show customer request details.
- Implement approval and rejection.

### Phase 5 — Notifications
- Configure email notifications.
- Configure WhatsApp notifications.
- Send notifications after an admin decision.

### Phase 6 — Testing and Deployment
- Test registration and login.
- Test request submission and history.
- Test admin approval and rejection.
- Test notifications.
- Deploy the application to Render.

## 10. Minimum Completion Requirements

The project is considered functional when:

1. Customers can register and log in.
2. Customers cannot submit requests without logging in.
3. Customers can submit service requests.
4. Customers can view their own request history and statuses.
5. The admin can log in and view all requests.
6. The admin dashboard displays accurate request counts.
7. The admin can approve or reject requests.
8. The customer receives email and WhatsApp notifications after a decision, subject to provider configuration.
9. Customer and admin access is properly protected.
10. The website and backend are deployed and working.

## Final Goal

Build a simple, working car wash request management website using the existing frontend, a Python FastAPI backend, and PostgreSQL. Focus on the required customer workflow, admin dashboard, approval/rejection process, and notifications. Avoid unnecessary features and complexity.
