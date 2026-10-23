# Render Deployment Plan — MrShine Car Wash

## 1. Overview

Deploy the MrShine Car Wash website, Python backend, and PostgreSQL database on Render.

The goal is to make the complete application accessible online so customers can register, log in, submit service requests, and track their request history. The administrator will manage requests through a dashboard.

We will keep the deployment simple by using two Render services.

## 2. Deployment Architecture

The application will consist of the following components:

### Service 1: Render Web Service

Hosts the Python FastAPI backend and serves the existing HTML website and additional customer/admin pages.

Responsibilities:
- Customer registration and login.
- Service request submission.
- Customer request history.
- Admin authentication.
- Admin dashboard and request management.
- Approval and rejection functionality.
- Email and WhatsApp notification integration.

### Service 2: Render PostgreSQL

Stores the application's data.

Responsibilities:
- Customer and admin accounts.
- Available services and prices.
- Customer service requests.
- Request statuses and timestamps.

### External Notification Providers

- Email service for approval/rejection notifications.
- WhatsApp Business Platform or an approved provider for WhatsApp notifications.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Frontend | Existing HTML, CSS, minimal JavaScript |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Hosting | Render |
| Version Control | GitHub |
| Email Notifications | Resend or another email provider |
| WhatsApp Notifications | WhatsApp Business Platform |

## 4. Deployment Strategy

We will build and test the application locally before deploying it.

### Step 1 — Develop Locally

- Create the FastAPI backend.
- Connect the backend to PostgreSQL.
- Implement customer registration and login.
- Implement service request submission.
- Build the customer dashboard.
- Build the admin dashboard.
- Implement request approval and rejection.
- Integrate email and WhatsApp notifications.

Verify that the core workflow works before deployment.

### Step 2 — Push the Code to GitHub

Store the complete application in a GitHub repository.

The repository should contain:
- Existing frontend files.
- Python backend.
- `requirements.txt`.
- Database models and configuration.
- Application documentation.

Add a `.gitignore` file to exclude:
- `.env`
- Virtual environment directories.
- Python cache files.
- Other local development files and secrets.

Never commit database passwords, authentication secrets, or notification API keys.

### Step 3 — Create a PostgreSQL Database on Render

1. Open the Render Dashboard.
2. Create a new PostgreSQL database.
3. Choose a suitable plan based on the project budget.
4. Select the same region as the backend service.
5. Wait for the database to become available.
6. Copy the database's internal connection URL.

The internal URL will be used by the backend to connect securely to PostgreSQL within Render.

Keep database credentials private.

### Step 4 — Create a Render Web Service

1. Open the Render Dashboard.
2. Select **New → Web Service**.
3. Connect the GitHub repository.
4. Select the repository containing the application.
5. Configure the runtime and deployment settings.
6. Set the build command to:

   ```bash
   pip install -r requirements.txt
   ```

7. Configure the start command according to the actual backend file structure.

   Example, if the FastAPI instance is named `app` inside `app/main.py`:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

8. Add the required environment variables.
9. Deploy the service.
10. Check the deployment logs for errors.

The exact start command will be confirmed once the project structure is finalized.

## 5. Environment Variables

Configure environment variables in the Render Web Service settings.

Example:

```env
DATABASE_URL=postgresql://USER:PASSWORD@INTERNAL_HOST/DATABASE
SECRET_KEY=your-secure-secret
CSRF_SECRET_KEY=your-secure-csrf-secret
APP_ENV=production
ADMIN_EMAIL=admin@your-domain.example
ADMIN_INITIAL_PASSWORD=<strong secret of at least 12 characters>
```

These values are examples only. Use the actual connection URL provided by Render and generate a strong secret for the application.

Configure `ADMIN_INITIAL_PASSWORD` as a deployment secret (at least 12 characters) to bootstrap the first production administrator. Do not use the development credentials listed in the README. On startup, the application disables a legacy administrator account if it still uses the published development password and no secure replacement is configured.

Important rules:
- Do not hard-code credentials in Python files.
- Do not commit `.env` files to GitHub.
- Do not expose database credentials or authentication secrets to frontend JavaScript.
- Use Render's internal database URL when the backend and database are in the same region.

## 6. Database Initialization

After creating the database and configuring the backend:

1. Configure the application to read `DATABASE_URL`.
2. Initialize the database schema using the selected database setup method.
3. Create the required tables.
4. Create the initial administrator account securely.
5. Add the initial service records.
6. Verify that the backend can read and write database records.

Use SQLAlchemy for database interaction. Use a simple, repeatable schema initialization or migration approach appropriate for the application.

## 7. Frontend and Backend Connection

The existing HTML website will communicate with FastAPI through API requests.

The backend will provide endpoints for:
- Registration and login.
- Retrieving services.
- Submitting customer requests.
- Retrieving customer request history.
- Retrieving admin dashboard statistics.
- Managing and deciding on requests.

The frontend must use the deployed backend URL when running in production.

If the frontend and backend are served by the same Render web service, use relative API paths where practical. This reduces the need for separate frontend hosting and CORS configuration.

## 8. Notifications

After the administrator approves or rejects a request:

1. Save the decision in PostgreSQL.
2. Attempt to send the email notification.
3. Attempt to send the WhatsApp notification.
4. Record the outcomes needed to identify failures.

Before production use:
- Configure the email provider.
- Configure the WhatsApp Business provider.
- Add the required credentials as environment variables.
- Complete any required WhatsApp business verification, template, and consent setup.

A notification failure must not undo the saved request decision.

## 9. Production Testing

After deployment, test the complete workflow.

### Customer Tests
- Register a new account.
- Log in and log out.
- Submit a service request.
- Confirm that the request is saved in PostgreSQL.
- View the request in the customer dashboard.
- Confirm that customers cannot access other customers' requests.

### Admin Tests
- Log in to the admin dashboard.
- View all requests.
- Verify total, pending, approved, and rejected counts.
- Approve a request.
- Reject another request.
- Verify that the statuses update correctly.

### Notification Tests
- Verify email notifications.
- Verify WhatsApp notifications.
- Check the provider response when a notification fails.
- Confirm that a saved decision remains intact when a notification fails.

### Deployment Tests
- Confirm that the public website loads.
- Confirm that API endpoints work.
- Check Render logs for application errors.
- Restart or redeploy the service and verify that database records remain available.

## 10. Cost Considerations

Check Render's current pricing before selecting the web service and PostgreSQL plans.

Important considerations:
- Free web services may spin down after inactivity and take longer to respond when started again.
- Database availability, storage, and backup features depend on the selected plan.
- Email and WhatsApp providers may have their own pricing, limits, and setup requirements.
- Choose a plan suitable for the client's expected usage and budget.

## 11. Final Deployment Checklist

- [ ] Application works locally.
- [ ] Code is pushed to GitHub.
- [ ] `.env` and secrets are excluded from Git.
- [ ] PostgreSQL database is created on Render.
- [ ] Render Web Service is configured.
- [ ] Build and start commands are correct.
- [ ] Environment variables are configured.
- [ ] Database schema is initialized.
- [ ] Initial admin account is created securely.
- [ ] Frontend is connected to the backend.
- [ ] Customer registration and login work.
- [ ] Service requests can be submitted.
- [ ] Admin approval and rejection work.
- [ ] Dashboard statistics are correct.
- [ ] Email and WhatsApp notifications are tested.
- [ ] Production logs are checked.
- [ ] Persistent database storage is verified.

## Final Goal

Deploy a simple, functional customer request management website using the existing frontend, FastAPI, PostgreSQL, and Render.

Build and test locally first, deploy the backend and database, connect the frontend, and verify the complete customer-to-admin workflow before handing the application to the client.
