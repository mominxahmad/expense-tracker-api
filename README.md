# Expense Tracker API

![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-00a393.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18+-4169E1.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange.svg)
![JWT](https://img.shields.io/badge/JWT-Authentication-black.svg)
![Status](https://img.shields.io/badge/Status-Learning-yellow.svg)

A REST API for managing personal expenses, built with **FastAPI, PostgreSQL, SQLAlchemy, and Alembic**.

I built this project while learning FastAPI and backend development. The main goal was to get practical experience with building an API, working with a real PostgreSQL database, implementing authentication and authorization, and managing database changes with migrations.

---

## What I Practiced

This project gave me hands-on practice with:

- FastAPI routing and dependencies
- Pydantic request validation
- PostgreSQL database integration
- SQLAlchemy ORM
- CRUD operations
- User registration and login
- Password hashing with bcrypt
- JWT authentication
- OAuth2 Bearer authentication
- User ownership and authorization
- Role-based access control
- Admin-only endpoints
- Alembic database migrations
- Environment variables
- Swagger / OpenAPI documentation

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Main programming language |
| **FastAPI** | API framework |
| **PostgreSQL** | Relational database |
| **SQLAlchemy** | ORM and database operations |
| **Pydantic** | Request validation and schemas |
| **Alembic** | Database migrations |
| **JWT** | Authentication |
| **bcrypt** | Password hashing |
| **Uvicorn** | ASGI server |

---

## Features

### Authentication

Users can create an account and log in to receive a JWT access token.

Passwords are hashed before being stored in the database rather than storing the original password.

Protected endpoints use Bearer token authentication.

### Expense Management

Authenticated users can:

- Create expenses
- View their own expenses
- View an individual expense
- Update their expenses
- Delete their expenses

Each expense is associated with the user who created it. When accessing the normal expense endpoints, users can only access their own expenses.

### Admin Authorization

The API also includes an `admin` role.

Admins can manage users and expenses through separate admin endpoints.

A newly registered account is automatically assigned the `user` role. Users cannot choose the `admin` role during registration.

Admins can later change a user's role between `user` and `admin`.

---

## API Reference

### Authentication

| HTTP Method | Endpoint | Description | Expected Status Codes |
|---|---|---|---|
| **POST** | `/auth/register` | Creates a new user account. | `201 Created`, `422 Unprocessable Entity` |
| **POST** | `/auth/login` | Authenticates a user and returns a JWT access token. | `200 OK`, `401 Unauthorized` |

### Expenses

These endpoints require authentication and operate only on the currently authenticated user's expenses.

| HTTP Method | Endpoint | Description | Expected Status Codes |
|---|---|---|---|
| **GET** | `/expenses/` | Retrieves all expenses belonging to the current user. | `200 OK` |
| **POST** | `/expenses/` | Creates a new expense for the current user. | `201 Created`, `422 Unprocessable Entity` |
| **GET** | `/expenses/{expense_id}` | Retrieves one of the current user's expenses. | `200 OK`, `404 Not Found` |
| **PUT** | `/expenses/{expense_id}` | Updates one of the current user's expenses. | `204 No Content`, `404 Not Found`, `422 Unprocessable Entity` |
| **DELETE** | `/expenses/{expense_id}` | Deletes one of the current user's expenses. | `204 No Content`, `404 Not Found` |

### Admin — Users

All of these endpoints require an authenticated admin account.

| HTTP Method | Endpoint | Description | Expected Status Codes |
|---|---|---|---|
| **GET** | `/admin/users` | Retrieves all users. | `200 OK`, `403 Forbidden` |
| **GET** | `/admin/users/{user_id}` | Retrieves a user by ID. | `200 OK`, `403 Forbidden`, `404 Not Found` |
| **PATCH** | `/admin/users/{user_id}/role` | Changes a user's role. | `200 OK`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity` |
| **DELETE** | `/admin/users/{user_id}` | Deletes a user and their associated expenses. | `204 No Content`, `403 Forbidden`, `404 Not Found` |

### Admin — Expenses

| HTTP Method | Endpoint | Description | Expected Status Codes |
|---|---|---|---|
| **GET** | `/admin/expenses` | Retrieves all expenses. | `200 OK`, `403 Forbidden` |
| **GET** | `/admin/expenses/{expense_id}` | Retrieves an expense by ID. | `200 OK`, `403 Forbidden`, `404 Not Found` |
| **GET** | `/admin/expenses/user/{user_id}` | Retrieves all expenses belonging to a specific user. | `200 OK`, `403 Forbidden`, `404 Not Found` |
| **DELETE** | `/admin/expenses/{expense_id}` | Deletes an expense by ID. | `204 No Content`, `403 Forbidden`, `404 Not Found` |

### API

| HTTP Method | Endpoint | Description | Expected Status Codes |
|---|---|---|---|
| **GET** | `/` | Returns basic API information. | `200 OK` |
| **GET** | `/health` | Returns the API health status. | `200 OK` |

---

## Authentication Flow

The authentication flow is based on JWT Bearer tokens.

```text
Register
   ↓
Password is hashed
   ↓
User stored in PostgreSQL
   ↓
Login
   ↓
Credentials verified
   ↓
JWT access token generated
   ↓
Token sent with protected requests
   ↓
FastAPI dependency verifies token
```

A protected request includes the token in the `Authorization` header:

```text
Authorization: Bearer <access_token>
```

The JWT contains information used by the API to identify the authenticated user and their role.

---

## Database

The API uses **PostgreSQL** as its database and **SQLAlchemy ORM** for database operations.

The database contains two main tables.

### `user`

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `email` | String | User email |
| `username` | String | Unique username |
| `first_name` | String | User's first name |
| `last_name` | String | User's last name |
| `hashed_password` | String | Hashed password |
| `role` | String | `user` or `admin` |

### `expense`

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `title` | String | Expense title |
| `amount` | Integer | Expense amount |
| `category` | String | Expense category |
| `description` | String | Optional description |
| `user_id` | Integer | Foreign key referencing `user.id` |

The relationship is simple:

```text
User
 │
 └───< Expense
        │
        └── user_id → user.id
```

One user can have multiple expenses, while each expense belongs to one user.

---

## SQLAlchemy

SQLAlchemy's ORM is used to interact with PostgreSQL through Python models.

For example, retrieving an expense belonging to the current user is handled through the SQLAlchemy model:

```python
db.query(Expense).filter(
    Expense.id == expense_id,
    Expense.user_id == user.get("id")
).first()
```

The `user_id` check is important because it prevents a regular user from accessing another user's expense simply by changing the `expense_id`.

---

## Alembic Migrations

I added **Alembic** to practice handling database schema changes.

The initial tables are currently created using SQLAlchemy's `create_all()` when the application starts.

For later schema changes, I use Alembic migrations.

The workflow is:

```text
Change SQLAlchemy model
        ↓
Create migration
        ↓
Write upgrade() / downgrade()
        ↓
Apply migration
```

Create a new revision:

```bash
alembic revision -m "Add phone column"
```

The generated migration is then written manually inside:

```text
alembic/versions/
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback the latest migration:

```bash
alembic downgrade -1
```

I used manual migrations here intentionally as part of learning how database schema changes are handled with Alembic.

---

## Project Structure

```text
expense-tracker-api/
├── main.py
├── database.py
├── models.py
├── requirements.txt
├── example.env
├── alembic.ini
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
└── routers/
    ├── auth.py
    ├── expenses.py
    └── admin.py
```

The application is separated into routers for authentication, regular expense operations, and admin operations.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/mominxahmad/expense-tracker-api.git
cd expense-tracker-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Create a PostgreSQL database named:

```text
ExpenseTrackerAPI
```

### 5. Create `.env`

Create a `.env` file using `example.env` as a reference:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ExpenseTrackerAPI
SECRET_KEY=YOUR_SECRET_KEY
ALGORITHM=HS256
```



### 6. Start the API

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## Interactive API Documentation

FastAPI automatically generates interactive documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to register users, log in, authorize with a JWT token, and test the protected endpoints directly from the browser.

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

### OpenAPI

```text
http://127.0.0.1:8000/openapi.json
```

### Screenshots

![Swagger UI](./assets/swaggerui1.png)
![Swagger UI](./assets/swaggerui2.png)
---

## Example Request

After logging in and obtaining an access token, an expense can be created with:

```bash
curl -X POST "http://127.0.0.1:8000/expenses/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lunch",
    "amount": 500,
    "category": "Food",
    "description": "Lunch with friends"
  }'
```

The API then stores the expense in PostgreSQL and associates it with the authenticated user.

---

## HTTP Status Codes

The API uses standard HTTP status codes for common situations:

| Status | Meaning |
|---|---|
| `200 OK` | Request completed successfully |
| `201 Created` | A new resource was created |
| `204 No Content` | Request succeeded without a response body |
| `401 Unauthorized` | Authentication failed or token is invalid |
| `403 Forbidden` | User is authenticated but does not have permission |
| `404 Not Found` | Requested resource does not exist |
| `422 Unprocessable Entity` | Request failed validation |

---

## Future Improvements

There are a few things I'd like to add as I continue improving my backend skills:

- Pytest tests
- Docker and Docker Compose
- CI/CD pipeline
- Pagination
- Expense filtering and sorting
- Expense dates and reporting
- Refresh tokens
- Better handling of monetary values using `Decimal` / `Numeric`
- More separated request and response schemas

---

## Why I Built This

This project was mainly about getting more comfortable with backend development as part of my Udemy FastAPI certification.

Instead of only following tutorials, I wanted to build something where I had to deal with an actual database, authentication, authorization, migrations, and different types of API endpoints.

It's still a learning project, but it gave me practical experience with several of the tools and concepts I want to use in future backend projects.