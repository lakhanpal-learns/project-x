# MrShine Backend Roadmap

## Goal

Make the Register and Login pages work with the backend and database.

## Technologies

- **Python** — to write backend code.
- **FastAPI** — to create API endpoints.
- **PostgreSQL** — to store user information.
- **SQLAlchemy** — to communicate with the database.

## Phase 1: Connect the Database

- Connect FastAPI to PostgreSQL.
- Store database settings in an environment file.
- Check whether the connection works.

**Result:** The backend can communicate with the database.

## Phase 2: Create the Users Table

Store these details for each user:

- User ID
- Full name
- Email address
- Phone number (optional)
- Hashed password
- Account creation date

Passwords will be stored securely as hashes, not as plain text.

**Result:** The database can store customer accounts.

## Phase 3: Build the Register API

Create this endpoint:

`POST /api/v1/auth/register`

It will:

1. Receive the user's registration details.
2. Check whether the email is already registered.
3. Check that the password meets the requirements.
4. Hash the password.
5. Save the new user in PostgreSQL.
6. Return a success or error message.

**Result:** Users can create accounts through the Register page.

## Phase 4: Build the Login API

Create this endpoint:

`POST /api/v1/auth/login`

It will:

1. Receive the user's email and password.
2. Find the account in the database.
3. Check the password.
4. Return an appropriate response.
5. Allow successful users to continue to the next page.

**Result:** Registered users can log in.

## Phase 5: Connect the Frontend

- Connect the Register form to the Register API.
- Connect the Login form to the Login API.
- Show clear success and error messages.
- Redirect users after successful login.

**Result:** The frontend and backend work together.

## Phase 6: Test Everything

Test these situations:

- Register a new user.
- Register with an email that already exists.
- Submit invalid information.
- Log in with the correct password.
- Log in with the wrong password.
- Check that passwords are not stored as plain text.
- Check that database errors are handled properly.

## Completion Checklist

- [ ] PostgreSQL connection works.
- [ ] Users table is created.
- [ ] Registration API works.
- [ ] Login API works.
- [ ] Frontend is connected to the APIs.
- [ ] All important tests pass.

## Development Rule

Complete one phase at a time. Test it before moving to the next phase.
