# HUSTLE

> **Connecting Nigeria's informal workforce to employers through real-time maps, AI-powered matching, and Squad-secured escrow payments.**

<div align="center">

![Flutter](https://img.shields.io/badge/Flutter-3.0+-02569B?logo=flutter&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)
![Squad](https://img.shields.io/badge/Squad-Payments-FF6B35)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)

</div>

---

## What is Hustle?

Over **80 million Nigerians** work in the informal economy — carrying blocks, fixing pipes, driving, cooking — yet they have no digital presence, no payment protection, and no financial history. Employers, on the other hand, rely on unreliable middlemen who charge markups and deliver inconsistently.

**Hustle bridges this gap:**

| Problem | Solution |
|---|---|
| Workers wait at roadsides with no way to find jobs | Real-time map showing jobs within 1–10 km |
| Employers can't verify workers or guarantee quality | AI trust score built from ratings, completion rate, and KYC |
| Workers get paid late, underpaid, or not at all | Squad escrow: funds locked on hire, released only on completion |
| Workers have no financial history for loans or insurance | Every completed job builds a verifiable digital work record |

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Technology Stack](#2-technology-stack)
3. [Repository Structure](#3-repository-structure)
4. [Backend Setup](#4-backend-setup)
   - [Prerequisites](#41-prerequisites)
   - [Installation](#42-installation)
   - [Environment Variables](#43-environment-variables)
   - [Database Setup](#44-database-setup)
   - [Running the Server](#45-running-the-server)
5. [Frontend Setup](#5-frontend-setup)
   - [Prerequisites](#51-prerequisites)
   - [Installation](#52-installation)
   - [Configuration](#53-configuration)
   - [Running the App](#54-running-the-app)
6. [Backend Architecture](#6-backend-architecture)
   - [Project Structure](#61-project-structure)
   - [API Endpoints](#62-api-endpoints)
   - [Authentication](#63-authentication)
   - [Payment System](#64-payment-system)
   - [Database Models](#65-database-models)
7. [Frontend Architecture](#7-frontend-architecture)
   - [Project Structure](#71-project-structure)
   - [State Management](#72-state-management)
   - [Navigation](#73-navigation)
   - [Networking](#74-networking)
8. [Feature Walkthroughs](#8-feature-walkthroughs)
   - [User Onboarding](#81-user-onboarding)
   - [Job Discovery](#82-job-discovery)
   - [Applying for a Job](#83-applying-for-a-job)
   - [Wallet Top-Up](#84-wallet-top-up)
   - [Worker Withdrawal](#85-worker-withdrawal)
   - [Escrow Flow](#86-escrow-flow)
9. [Design System](#9-design-system)
10. [Testing & Debugging](#10-testing--debugging)
11. [Deployment](#11-deployment)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Flutter App (iOS/Android)               │
│                                                             │
│   Auth ─── Discovery ─── Profile ─── Wallet ─── Map        │
└────────────────────┬────────────────────────────────────────┘
                     │  HTTPS + Supabase JWT
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Python 3.13)                  │
│                                                             │
│   /auth  /jobs  /applications  /wallet  /escrow  /webhook   │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────┐      ┌──────────────────────────────────┐
│    Supabase      │      │         Squad API (GTBank)        │
│                  │      │                                   │
│  PostgreSQL DB   │      │  Virtual Accounts  Transfer API   │
│  Auth (JWT)      │      │  Webhooks          Simulate Pay   │
│  PostGIS         │      └──────────────────────────────────┘
└──────────────────┘
```

**Request lifecycle:**

1. Flutter sends a request with a Supabase JWT in the `Authorization` header
2. FastAPI verifies the JWT using Supabase's public JWKS endpoint (cached on startup)
3. Business logic runs — jobs fetched, applications created, escrow locked, etc.
4. Squad API handles all money movement; Squad fires webhooks back to FastAPI
5. FastAPI updates the database; Flutter polls for state changes

---

## 2. Technology Stack

### Backend

| Layer | Technology | Purpose |
|---|---|---|
| Framework | **FastAPI** (Python 3.13) | REST API, async, auto-docs |
| Database | **PostgreSQL** via Supabase | Primary data store |
| ORM | **SQLAlchemy** (async + asyncpg) | Database queries |
| Auth | **Supabase Auth** (ES256 JWT) | Token verification |
| Payments | **Squad API** (GTBank) | VA, escrow, transfers |
| Location | **PostGIS** | Geospatial job queries |
| Server | **Uvicorn** | ASGI server |

### Frontend

| Layer | Technology | Purpose |
|---|---|---|
| Framework | **Flutter** (Dart) | Cross-platform mobile |
| State | **Riverpod** (`flutter_riverpod`) | Async state management |
| Navigation | **GoRouter** | Declarative routing |
| HTTP | **Dio** | API calls + interceptors |
| Auth | **Supabase Flutter SDK** | Google Sign-In, JWT |
| Maps | **flutter_map** + OpenStreetMap | Job location map |
| Fonts | **Syne** · **DM Sans** | Typography |

---

## 3. Repository Structure

```
hustle/
│
├── backend/                    # FastAPI backend
│   ├── .env                    # Environment variables (not committed)
│   ├── requirements.txt        # Python dependencies
│   └── app/
│       ├── main.py             # FastAPI app, middleware, router registration
│       ├── dependencies.py     # JWT auth, role guards
│       ├── api/v1/endpoints/   # Route handlers
│       ├── db/                 # SQLAlchemy models and session
│       ├── services/           # Business logic
│       └── core/               # Config, middleware
│
└── lib/                        # Flutter frontend (inside Flutter project root)
    ├── core/                   # App-wide config, routing, networking
    ├── features/               # Feature modules
    └── shared/                 # Reusable widgets
```

---

## 4. Backend Setup

### 4.1 Prerequisites

- **Python 3.13** — [Download](https://python.org/downloads)
- **pip** (comes with Python)
- A **Supabase** project — [Create one free](https://supabase.com)
- A **Squad** sandbox account — [Sign up](https://sandbox.squadco.com)
- **ngrok** (for local webhook testing) — [Download](https://ngrok.com/download)

### 4.2 Installation

```bash
# Navigate to the backend directory
cd hustle/backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Install all dependencies
pip install -r requirements.txt
```

### 4.3 Environment Variables

Create a `.env` file in the `backend/` directory. **Each variable must be on its own line with no trailing spaces.**

```env
# ── Database ──────────────────────────────────────────────────
HUSTLE_DATABASE_URL=postgresql+asyncpg://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-eu-west-3.pooler.supabase.com:5432/postgres?prepared_statement_cache_size=0

# ── Supabase ──────────────────────────────────────────────────
HUSTLE_SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
HUSTLE_SUPABASE_ANON_KEY=your_supabase_anon_key
HUSTLE_SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# ── JWT ───────────────────────────────────────────────────────
HUSTLE_JWT_SECRET=your_supabase_jwt_secret

# ── Squad Payments ────────────────────────────────────────────
HUSTLE_SQUAD_SECRET_KEY=sandbox_sk_your_key_here
HUSTLE_SQUAD_WEBHOOK_SECRET=sandbox_sk_your_key_here
HUSTLE_SQUAD_BASE_URL=https://sandbox-api-d.squadco.com

# ── App ───────────────────────────────────────────────────────
API_BASE_URL=https://your-ngrok-subdomain.ngrok-free.app
```

**Where to find these values:**

| Variable | Location |
|---|---|
| `HUSTLE_DATABASE_URL` | Supabase → Settings → Database → Connection string (Transaction mode) |
| `HUSTLE_SUPABASE_URL` | Supabase → Settings → API → Project URL |
| `HUSTLE_SUPABASE_ANON_KEY` | Supabase → Settings → API → `anon` key |
| `HUSTLE_SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → `service_role` key |
| `HUSTLE_JWT_SECRET` | Supabase → Settings → API → JWT Secret |
| `HUSTLE_SQUAD_SECRET_KEY` | sandbox.squadco.com → Settings → API & Webhook |
| `API_BASE_URL` | Your running ngrok tunnel URL |

### 4.4 Database Setup

All tables are managed in Supabase. Run the following SQL in the **Supabase SQL Editor**:

```sql
-- Enable PostGIS for location queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Users
CREATE TABLE IF NOT EXISTS users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT UNIQUE NOT NULL,
  phone       TEXT,
  full_name   TEXT,
  avatar_url  TEXT,
  role        TEXT,               -- 'worker' or 'employer'
  nin         TEXT,
  kyc_status  TEXT DEFAULT 'unverified',
  is_active   BOOLEAN DEFAULT true,
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Worker Profiles
CREATE TABLE IF NOT EXISTS worker_profiles (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  skills           TEXT[] DEFAULT '{}',
  experience_level TEXT DEFAULT 'entry',
  job_radius_km    INTEGER DEFAULT 5,
  availability     TEXT DEFAULT 'both',
  bio              TEXT,
  trust_score      FLOAT DEFAULT 50.0,
  completion_rate  FLOAT DEFAULT 0.0,
  avg_rating       FLOAT DEFAULT 0.0,
  total_jobs       INTEGER DEFAULT 0,
  disputes_count   INTEGER DEFAULT 0,
  is_verified      BOOLEAN DEFAULT false,
  is_available     BOOLEAN DEFAULT true,
  fcm_token        TEXT,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

-- Employer Profiles
CREATE TABLE IF NOT EXISTS employer_profiles (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  company_name TEXT,
  industry     TEXT,
  created_at   TIMESTAMPTZ DEFAULT now(),
  updated_at   TIMESTAMPTZ DEFAULT now()
);

-- Jobs
CREATE TABLE IF NOT EXISTS jobs (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employer_id    UUID REFERENCES users(id) ON DELETE CASCADE,
  title          TEXT NOT NULL,
  description    TEXT,
  category       TEXT,
  pay_kobo       BIGINT NOT NULL,
  latitude       FLOAT,
  longitude      FLOAT,
  location_name  TEXT,
  status         TEXT DEFAULT 'open',
  expires_at     TIMESTAMPTZ,
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now()
);

-- Applications
CREATE TABLE IF NOT EXISTS applications (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id         UUID REFERENCES jobs(id) ON DELETE CASCADE,
  worker_id      UUID REFERENCES users(id) ON DELETE CASCADE,
  cover_letter   TEXT,
  proposed_rate  NUMERIC,
  is_accepted    BOOLEAN DEFAULT false,
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now()
);

-- Employer Wallets
CREATE TABLE IF NOT EXISTS employer_wallets (
  user_id         UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  available_kobo  BIGINT DEFAULT 0,
  locked_kobo     BIGINT DEFAULT 0,
  total_spent     BIGINT DEFAULT 0,
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Worker Wallets
CREATE TABLE IF NOT EXISTS worker_wallets (
  user_id          UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  available_kobo   BIGINT DEFAULT 0,
  total_earned     BIGINT DEFAULT 0,
  total_withdrawn  BIGINT DEFAULT 0,
  updated_at       TIMESTAMPTZ DEFAULT now()
);

-- Wallet Transactions
CREATE TABLE IF NOT EXISTS wallet_transactions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  type          TEXT NOT NULL,
  amount        BIGINT NOT NULL,
  amount_kobo   BIGINT,
  balance_after BIGINT NOT NULL,
  reference     TEXT UNIQUE,
  description   TEXT,
  job_id        UUID,
  escrow_id     UUID,
  status        TEXT DEFAULT 'completed',
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- Escrow Records
CREATE TABLE IF NOT EXISTS escrow_records (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id              TEXT NOT NULL,
  employer_id         UUID REFERENCES users(id),
  worker_id           UUID REFERENCES users(id),
  total_kobo          BIGINT NOT NULL,
  worker_amount_kobo  BIGINT NOT NULL,
  platform_fee_kobo   BIGINT NOT NULL,
  status              TEXT DEFAULT 'pending',
  squad_ref           TEXT,
  released_at         TIMESTAMPTZ,
  created_at          TIMESTAMPTZ DEFAULT now()
);

-- Withdrawals
CREATE TABLE IF NOT EXISTS withdrawals (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id),
  amount_kobo     BIGINT NOT NULL,
  bank_code       TEXT NOT NULL,
  account_number  TEXT NOT NULL,
  account_name    TEXT,
  squad_ref       TEXT UNIQUE,
  status          TEXT DEFAULT 'pending',
  failure_reason  TEXT,
  initiated_at    TIMESTAMPTZ DEFAULT now(),
  completed_at    TIMESTAMPTZ
);

-- Ratings
CREATE TABLE IF NOT EXISTS ratings (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rater_id   UUID REFERENCES users(id),
  rated_id   UUID REFERENCES users(id),
  job_id     UUID REFERENCES jobs(id),
  score      FLOAT NOT NULL CHECK (score BETWEEN 1 AND 5),
  comment    TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 4.5 Running the Server

```bash
# Make sure you're in the backend directory with venv activated
cd hustle/backend
source venv/bin/activate

# Start with hot reload (development)
uvicorn app.main:app --reload --port 8000

# Start without reload (production-like)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server starts at `http://localhost:8000`.

**Interactive API docs:** `http://localhost:8000/docs`
**Health check:** `http://localhost:8000/health/live`

#### Setting Up ngrok (for Squad Webhooks)

Squad must be able to reach your local server. Use ngrok to create a public tunnel:

```bash
# Start tunnel
ngrok http 8000

# You'll see a URL like:
# https://xxxx-xx-xx.ngrok-free.app

# Update .env:
# API_BASE_URL=https://xxxx-xx-xx.ngrok-free.app

# Set this as your webhook URL in Squad sandbox dashboard:
# https://xxxx-xx-xx.ngrok-free.app/api/v1/webhook/squad
```

---

## 5. Frontend Setup

### 5.1 Prerequisites

- **Flutter SDK 3.0+** — [Install Flutter](https://flutter.dev/docs/get-started/install)
- **Dart SDK 3.0+** (bundled with Flutter)
- **Xcode 14+** for iOS development
- **Android Studio** for Android development
- **CocoaPods** for iOS dependencies: `sudo gem install cocoapods`

Verify your setup:

```bash
flutter doctor
```

All items should show a green checkmark before proceeding.

### 5.2 Installation

```bash
# Navigate to the Flutter project root
cd hustle

# Install Flutter dependencies
flutter pub get

# iOS only — install CocoaPods dependencies
cd ios && pod install && cd ..
```

### 5.3 Configuration

#### Set the Backend URL

Open `lib/core/config/env.dart` and update the base URL:

```dart
class Env {
  // Replace with your ngrok URL or deployed backend URL
  static const apiBaseUrl = 'https://your-ngrok-url.ngrok-free.app';
}
```

#### Configure Supabase

Open `lib/main.dart` and ensure Supabase is initialized with your project credentials:

```dart
await Supabase.initialize(
  url:    'https://YOUR_PROJECT_REF.supabase.co',
  anonKey: 'your_supabase_anon_key',
);
```

#### Enable Google Sign-In

**iOS:**
1. Add your `GoogleService-Info.plist` to `ios/Runner/`
2. In Supabase → Auth → Providers → Google, add your iOS bundle ID as a redirect URL:
   ```
   com.yourcompany.hustle://login-callback
   ```

**Android:**
1. Add your `google-services.json` to `android/app/`
2. Add SHA-1 fingerprint in Supabase → Auth → Providers → Google

### 5.4 Running the App

```bash
# List available devices
flutter devices

# Run on iOS Simulator
flutter run -d iPhone

# Run on Android Emulator
flutter run -d emulator-5554

# Run on a physical device
flutter run -d your-device-id

# Run with a specific backend URL (without editing env.dart)
flutter run --dart-define=API_BASE_URL=https://your-ngrok-url.ngrok-free.app
```

#### Setting Mock Location (Emulator/Simulator)

The app uses GPS to show nearby jobs. Set a Lagos location for testing:

**iOS Simulator:**
```
Simulator menu bar → Features → Location → Custom Location
Latitude:  6.5244
Longitude: 3.3792
```

**Android Emulator:**
```bash
adb emu geo fix 3.3792 6.5244
```

---

## 6. Backend Architecture

### 6.1 Project Structure

```
backend/
├── .env                              # Environment variables
├── requirements.txt                  # Dependencies
└── app/
    ├── main.py                       # App factory, middleware, router registration
    ├── dependencies.py               # JWT verification, role guards
    │
    ├── core/
    │   ├── config.py                 # Settings (reads from .env with HUSTLE_ prefix)
    │   └── middleware.py             # Request timing middleware
    │
    ├── api/
    │   └── v1/
    │       └── endpoints/
    │           ├── auth.py           # /role, /me, /kyc/submit
    │           ├── jobs.py           # CRUD + /nearby
    │           ├── applications.py   # apply, accept, reject
    │           ├── escrow.py         # /lock, /release, status
    │           ├── wallet.py         # balance, VA, transactions, withdraw
    │           ├── webhook.py        # Squad payment webhook handler
    │           ├── profile.py        # worker/employer profile GET+PUT
    │           ├── ratings.py        # POST rating, GET by user
    │           ├── match.py          # AI matching endpoints
    │           ├── feedback.py       # Feedback submission
    │           └── health.py         # /live, /ready
    │
    ├── db/
    │   ├── base.py                   # Declarative base
    │   ├── session.py                # Async engine + session factory (NullPool)
    │   ├── init_db.py                # Startup validation
    │   ├── types.py                  # Custom GUID type for UUID
    │   └── models/
    │       ├── user.py
    │       ├── job.py
    │       ├── application.py
    │       ├── worker_profile.py
    │       ├── employer_profile.py
    │       ├── wallet.py             # EmployerWallet, WorkerWallet, WalletTransaction, Withdrawal, EscrowRecord
    │       ├── rating.py
    │       └── match_log.py
    │
    └── services/
        ├── auth_service.py           # get_or_create_user
        ├── squad_service.py          # VA creation, simulate, transfer, verify webhook
        ├── escrow_service.py         # credit_wallet, lock_funds, release_escrow, initiate_withdrawal
        └── kyc_service.py            # NIN verification logic
```

### 6.2 API Endpoints

#### Authentication — `/api/v1/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/role` | ✅ | Set worker or employer role (one-time) |
| `GET` | `/auth/me` | ✅ | Get current user info + role |
| `POST` | `/auth/kyc/submit` | ✅ | Submit NIN for verification |

#### Jobs — `/api/v1/jobs`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/jobs/nearby` | ✅ | Get jobs within radius of user's coordinates |
| `POST` | `/jobs` | ✅ Employer | Create a new job posting |
| `GET` | `/jobs/{id}` | ✅ | Get single job details |
| `GET` | `/jobs/my-posts` | ✅ Employer | Get employer's posted jobs |
| `POST` | `/jobs/{id}/complete` | ✅ Employer | Mark job as completed |
| `POST` | `/jobs/{id}/cancel` | ✅ Employer | Cancel a job posting |

#### Applications — `/api/v1/applications`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/applications` | ✅ Worker | Apply for a job |
| `GET` | `/applications/my` | ✅ Worker | Get all my applications |
| `GET` | `/applications/job/{id}` | ✅ Employer | Get all applications for a job |
| `POST` | `/applications/{id}/accept` | ✅ Employer | Accept an application |
| `POST` | `/applications/{id}/reject` | ✅ Employer | Reject an application |

#### Wallet — `/api/v1/wallet`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/wallet/balance` | ✅ | Get current wallet balance |
| `GET` | `/wallet/transactions` | ✅ | Get transaction history |
| `GET` | `/wallet/virtual-account` | ✅ Employer | Get Squad VA for top-up |
| `POST` | `/wallet/virtual-account` | ✅ Employer | Create Squad VA (first time) |
| `POST` | `/wallet/lookup` | ✅ Worker | Verify bank account before withdrawal |
| `POST` | `/wallet/withdraw` | ✅ Worker | Withdraw earnings to bank |
| `POST` | `/wallet/simulate-payment` | ✅ | Trigger fake payment (sandbox only) |

#### Escrow — `/api/v1/escrow`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/escrow/lock` | ✅ Employer | Lock funds when hiring a worker |
| `POST` | `/escrow/release` | ✅ Employer | Release funds to worker on completion |
| `GET` | `/escrow/{job_id}` | ✅ | Get escrow status for a job |

#### Profiles — `/api/v1/profile`

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/profile/worker` | ✅ | Get my worker profile |
| `PUT` | `/profile/worker` | ✅ Worker | Update skills, availability, bio |
| `GET` | `/profile/worker/{user_id}` | ✅ | Get any worker's public profile |
| `GET` | `/profile/employer` | ✅ | Get my employer profile |
| `PUT` | `/profile/employer` | ✅ Employer | Update company info |

#### Ratings — `/api/v1/ratings`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/ratings` | ✅ | Submit a rating after job completion |
| `GET` | `/ratings/{user_id}` | ✅ | Get all ratings for a user |

#### Webhooks — `/api/v1/webhook`

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/webhook/squad` | None | Receive Squad payment notifications |

#### Health — `/health`

| Method | Path | Description |
|---|---|---|
| `GET` | `/health/live` | Liveness check |
| `GET` | `/health/ready` | Readiness check (DB connection) |

### 6.3 Authentication

Hustle uses **Supabase Auth with Google Sign-In**. The backend verifies JWTs using ES256 (Supabase's JWKS endpoint).

```python
# dependencies.py — simplified flow
async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    # 1. Decode JWT using cached Supabase public key
    payload = jwt.decode(token, public_key, algorithms=["ES256"])

    # 2. Extract user ID from 'sub' claim
    user_id = payload["sub"]

    # 3. Get or create user in our database
    user, created = await get_or_create_user(db, user_id, email, full_name, avatar_url)

    return user
```

**Key decisions:**
- The public key is fetched from Supabase's JWKS endpoint **once at startup** and cached — not on every request (avoids 2500ms latency per call)
- `get_or_create_user` first checks by UUID, then by email as fallback — prevents duplicate key violations when the same Google account logs in with a different UUID

### 6.4 Payment System

All payments flow through **Squad API** — a GTBank product. Hustle is designed to operate as a **future GTBank subsidiary**, leveraging GTBank's banking licence to run a regulated escrow system.

#### Fee Model

```
Employer pays: Job Value + 2% Platform Fee
Worker receives: 100% of Job Value
Hustle keeps: 2% Platform Fee
```

#### Virtual Account Flow

```
1. Employer calls GET /wallet/virtual-account
      │── Returns permanent VA number (e.g. GTBank 6887789875)
      │
2. Employer transfers money from their bank app to the VA
      │
3. Squad detects the transfer and fires a webhook
      POST /api/v1/webhook/squad
      {
        "transaction_indicator": "C",
        "customer_identifier": "HUSTLE_89ABB3F8",
        "principal_amount": "100000.00"
      }
      │
4. Backend credits the employer wallet
      employer_wallets.available_kobo += amount
      │
5. Flutter detects balance change via 5-second polling
      GET /wallet/balance → balance increased → show success dialog
```

#### Escrow Flow

```
1. Employer posts a job and hires a worker
      POST /escrow/lock { job_id, worker_id, job_value_kobo }
      │── employer_wallets.available_kobo -= (job_value + 2% fee)
      │── employer_wallets.locked_kobo    += (job_value + 2% fee)
      │── Creates EscrowRecord with status "locked"
      │
2. Worker completes the work
      │
3. Employer confirms completion
      POST /escrow/release { job_id }
      │── escrow_records.status = "released"
      │── employer_wallets.locked_kobo -= total
      │── worker_wallets.available_kobo += job_value (100%)
      │── Platform retains the 2% fee
```

### 6.5 Database Models

#### Core Relationships

```
users
  ├── worker_profiles (1:1)
  ├── employer_profiles (1:1)
  ├── employer_wallets (1:1)
  ├── worker_wallets (1:1)
  ├── jobs (1:many — as employer)
  ├── applications (1:many — as worker)
  ├── ratings_given (1:many — as rater)
  └── ratings_received (1:many — as rated)

jobs
  ├── applications (1:many)
  └── escrow_records (1:1)
```

#### Key Column Types

| Model | Column | DB Type | SQLAlchemy Type |
|---|---|---|---|
| `WorkerProfile` | `skills` | `text[]` | `ARRAY(Text)` |
| `WalletTransaction` | `amount` | `bigint NOT NULL` | `BigInteger` |
| `WalletTransaction` | `job_id` | `uuid` | `GUID()` |
| `EmployerWallet` | PK | `user_id` (no `id` column) | `primary_key=True` on `user_id` |

> **All monetary values are stored in kobo (1 Naira = 100 kobo).** This avoids floating-point precision issues with financial data.

---

## 7. Frontend Architecture

### 7.1 Project Structure

```
lib/
├── main.dart                          # App entry, Supabase init, ProviderScope
│
├── core/
│   ├── config/
│   │   ├── theme.dart                 # AppColors, text styles
│   │   └── env.dart                   # API base URL
│   ├── network/
│   │   ├── dio_client.dart            # Singleton Dio instance
│   │   └── interceptors/
│   │       └── auth_interceptor.dart  # Attaches JWT to every request
│   ├── router/
│   │   ├── app_router.dart            # GoRouter config + auth guard
│   │   └── routes.dart                # Route name constants
│   └── utils/
│       └── formatters.dart            # Naira, date, distance formatters
│
├── features/
│   ├── auth/
│   │   └── presentation/screens/
│   │       ├── phone_auth_screen.dart     # Google Sign-In
│   │       ├── role_select_screen.dart    # Worker vs Employer
│   │       └── kyc_screen.dart            # NIN submission
│   │
│   ├── onboarding/
│   │   └── presentation/screens/
│   │       ├── splash_screen.dart         # Auth check + routing
│   │       └── worker_setup_screen.dart   # Skills + availability
│   │
│   ├── discovery/
│   │   ├── data/
│   │   │   └── job_model.dart             # JobListing, JobFilter, enums
│   │   └── presentation/
│   │       ├── providers/
│   │       │   ├── jobs_provider.dart     # Fetches /jobs/nearby
│   │       │   └── filter_provider.dart   # Active filter + view toggle
│   │       └── screens/
│   │           └── discovery_screen.dart  # Header, trust banner, job list
│   │
│   ├── map/
│   │   └── presentation/screens/
│   │       └── map_screen.dart            # flutter_map with job pins
│   │
│   ├── profile/
│   │   ├── data/models/
│   │   │   └── profile_model.dart         # WorkerProfile, WorkerReview
│   │   └── presentation/
│   │       ├── providers/
│   │       │   └── profile_provider.dart  # Fetches /profile/worker + /ratings
│   │       └── screens/
│   │           └── worker_profile_screen.dart
│   │
│   └── wallet/
│       └── presentation/
│           ├── providers/
│           │   └── wallet_provider.dart   # Balance + transaction state
│           └── screens/
│               ├── wallet_screen.dart     # Balance + history
│               ├── topup_screen.dart      # VA display + polling
│               └── withdrawal_screen.dart # Bank lookup + withdraw
│
└── shared/
    └── widgets/
        └── skill_chip.dart                # Filled / outlined skill pill
```

### 7.2 State Management

Hustle uses **Riverpod** with `AsyncNotifier<T>` for all server-dependent state.

#### The Pattern

```dart
// 1. Define the notifier
class JobsNotifier extends AsyncNotifier<List<JobListing>> {
  @override
  Future<List<JobListing>> build() => _fetch();

  Future<List<JobListing>> _fetch() async {
    final position = await Geolocator.getCurrentPosition();
    final response = await DioClient.instance.get(
      '/api/v1/jobs/nearby',
      queryParameters: {
        'lat': position.latitude,
        'lng': position.longitude,
        'radius_km': 10,
      },
    );
    return (response.data['data'] as List)
        .map((j) => JobListing.fromJson(j))
        .toList();
  }

  Future<void> applyFilter(JobFilter filter) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_fetch);
  }
}

// 2. Register the provider
final jobsProvider = AsyncNotifierProvider<JobsNotifier, List<JobListing>>(
  JobsNotifier.new,
);

// 3. Consume in a widget
class _JobsList extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobsAsync = ref.watch(jobsProvider);

    return jobsAsync.when(
      loading: () => const CircularProgressIndicator(),
      error:   (e, _) => Text('Error: $e'),
      data:    (jobs) => ListView(children: jobs.map(_JobCard.new).toList()),
    );
  }
}
```

#### All Providers

| Provider | State Type | Purpose |
|---|---|---|
| `profileProvider` | `AsyncNotifier<WorkerProfile>` | Worker profile + reviews |
| `jobsProvider` | `AsyncNotifier<List<JobListing>>` | Nearby jobs list |
| `walletProvider` | `AsyncNotifier<WalletState>` | Balance + transactions |
| `filterProvider` | `Notifier<JobFilter>` | Active filter (Nearby / Top Paying / Urgent) |
| `viewToggleProvider` | `Notifier<bool>` | List vs Map toggle |

### 7.3 Navigation

GoRouter provides declarative routing with an auth guard that redirects unauthenticated users automatically.

```dart
// routes.dart
class Routes {
  static const splash     = '/';
  static const roleSelect = '/role-select';
  static const kyc        = '/kyc';
  static const discovery  = '/discovery';
  static const mapView    = '/map';
  static const jobDetail  = '/jobs/:id';
  static const profile    = '/profile';
  static const wallet     = '/wallet';
  static const topUp      = '/wallet/topup';
  static const withdrawal = '/wallet/withdraw';
}
```

**Auth guard logic:**

```
Any navigation attempt
    │
    ▼
Check Supabase.instance.client.auth.currentSession
    │
    ├── null → redirect to /  (splash/sign-in)
    └── valid → proceed
```

### 7.4 Networking

#### DioClient

```dart
// lib/core/network/dio_client.dart
class DioClient {
  static final instance = Dio(
    BaseOptions(
      baseUrl:        Env.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers:        {'Content-Type': 'application/json'},
    ),
  )..interceptors.add(AuthInterceptor());
}
```

#### Auth Interceptor

```dart
// lib/core/network/interceptors/auth_interceptor.dart
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final session = Supabase.instance.client.auth.currentSession;
    if (session != null) {
      options.headers['Authorization'] = 'Bearer ${session.accessToken}';
    }
    handler.next(options);
  }
}
```

Every API call automatically carries the current Supabase JWT — no manual token management needed anywhere in the app.

---

## 8. Feature Walkthroughs

### 8.1 User Onboarding

```
Install App
    │
    ▼
Splash Screen → checks Supabase session
    │
    ├── No session ─────────────────────────────────────────────▶ Google Sign-In
    │                                                                    │
    │                                                            Supabase OAuth
    │                                                                    │
    │                                                            Role Select Screen
    │                                                           ┌────────┴────────┐
    │                                                       Worker            Employer
    │                                                           │                 │
    │                                                      Worker Setup      Wallet Screen
    │                                                    (skills, radius)
    │                                                           │
    │                                                      Discovery Screen
    │
    └── Has session → check user.role → route to correct home screen
```

### 8.2 Job Discovery

1. Worker opens app → lands on Discovery Screen
2. App calls `GET /api/v1/jobs/nearby?lat=6.52&lng=3.38&radius_km=10`
3. Jobs appear as cards sorted by distance
4. Worker taps filter tabs: **Nearby** / **Top Paying** / **Urgent**
5. Worker taps map icon to switch to map view with job pins
6. Each card shows: title, location, pay in Naira, distance, escrow badge, star rating

### 8.3 Applying for a Job

1. Worker taps **"Quick Apply"** or **"Apply Now"** on a job card
2. Flutter calls `POST /api/v1/applications { "job_id": "uuid" }`
3. Backend verifies worker role + checks for duplicate application
4. On success: button changes to **"✅ Applied"**
5. On duplicate: snackbar shows "Already applied for this job"
6. Employer sees the application in their dashboard via `GET /api/v1/applications/job/{id}`

### 8.4 Wallet Top-Up

```
Employer opens Top Up Screen
    │
    ▼
Enters amount (min ₦1,000) → taps "Generate Account"
    │
    ▼
GET /api/v1/wallet/virtual-account
    │── Returns: { bank: "GTBank", account_number: "6887789875", account_name: "Hustle Platform" }
    │
    ▼
Screen displays account details for transfer
    │
    ▼ (Flutter starts polling every 5 seconds)
    │
Employer transfers money from their bank app
    │
    ▼
Squad fires webhook → POST /api/v1/webhook/squad
    │── Backend: employer_wallets.available_kobo += amount
    │
    ▼
Flutter polling detects balance increase
    │── Shows "Payment Received! ₦X,XXX added to your wallet"
```

### 8.5 Worker Withdrawal

1. Worker opens Withdrawal Screen
2. Selects bank and enters account number
3. Flutter calls `POST /api/v1/wallet/lookup` — shows verified account name
4. Worker confirms and taps Withdraw
5. Flutter calls `POST /api/v1/wallet/withdraw { bank_code, account_number, amount_kobo }`
6. Backend deducts from worker wallet immediately (held during processing)
7. Squad Transfer API sends money to worker's bank account
8. On failure: worker wallet is automatically refunded

### 8.6 Escrow Flow

```
Employer posts a job
    │
Worker applies → Employer accepts application
    │
    ▼
POST /api/v1/escrow/lock
    {
      "job_id": "uuid",
      "worker_id": "uuid",
      "job_value_kobo": 500000
    }
    │── Deducts ₦5,000 + ₦100 fee (2%) = ₦5,100 from employer wallet
    │── Locks ₦5,100 in escrow
    │
Work is completed
    │
    ▼
POST /api/v1/escrow/release { "job_id": "uuid" }
    │── Worker receives ₦5,000 (100% of job value)
    │── Hustle retains ₦100 (2% platform fee)
    │── Escrow record marked "released"
    │
    ▼
Worker sees updated balance → can withdraw to bank
```

---

## 9. Design System

### Colors

```dart
class AppColors {
  // Brand
  static const primaryGreen      = Color(0xFF1A7A4A);  // Main green
  static const primaryGreenLight = Color(0xFFE8F5EE);  // Light green background

  // Text
  static const textPrimary   = Color(0xFF1A1A2E);      // Near black
  static const textSecondary = Color(0xFF6B7280);      // Medium grey
  static const textHint      = Color(0xFF9CA3AF);      // Light grey

  // Backgrounds
  static const backgroundWhite = Color(0xFFFFFFFF);
  static const backgroundGrey  = Color(0xFFF3F4F6);

  // Utility
  static const borderLight = Color(0xFFE5E7EB);
  static const success     = Color(0xFF22C55E);
  static const accentRed   = Color(0xFFEF4444);
  static const starColor   = Color(0xFFFFB800);
}
```

### Typography

| Element | Font | Size | Weight |
|---|---|---|---|
| Screen titles | Syne | 22–28pt | 700 |
| Card headings | DM Sans | 14–16pt | 700 |
| Body text | DM Sans | 12–14pt | 400 |
| Captions | DM Sans | 11–12pt | 400 |
| Stats / prices | Syne | 15–36pt | 800 |
| Buttons | DM Sans | 13–16pt | 700 |

### Reusable Widgets

| Widget | File | Description |
|---|---|---|
| `SkillChip` | `shared/widgets/skill_chip.dart` | Filled or outlined skill tag |
| `_TagPill` | `discovery_screen.dart` | Urgency, escrow, distance badges |
| `_StarRow` | `discovery_screen.dart` | 5-star rating row |
| `_TrustScoreCircle` | `worker_profile_screen.dart` | Circular score ring |
| `_FeeBreakdown` | `discovery_screen.dart` | Job value + fee breakdown card |
| `_DetailRow` | `topup_screen.dart` | Label–value pair in info cards |

---

## 10. Testing & Debugging

### Backend — Manual Testing

The FastAPI auto-docs at `http://localhost:8000/docs` let you test every endpoint with a built-in UI.

```bash
# Get your JWT from Flutter (print it in the AuthInterceptor)
# Then authorize in Swagger: click "Authorize" → paste the token

# Quick health check
curl http://localhost:8000/health/live

# Set role (replace TOKEN with actual JWT)
curl -X POST http://localhost:8000/api/v1/auth/role \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "worker"}'

# Simulate a wallet top-up (sandbox only)
curl -X POST http://localhost:8000/api/v1/webhook/squad \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_indicator": "C",
    "customer_identifier": "HUSTLE_89ABB3F8",
    "principal_amount": "10000.00",
    "transaction_reference": "TEST_001"
  }'
```

### Backend — Checking Database

Run these queries in the Supabase SQL Editor:

```sql
-- See all users and their roles
SELECT id, email, role, kyc_status FROM users;

-- Check worker profiles
SELECT user_id, skills, trust_score, total_jobs FROM worker_profiles;

-- Check wallet balances
SELECT user_id, available_kobo, locked_kobo FROM employer_wallets;

-- See recent transactions
SELECT user_id, type, amount, description, created_at
FROM wallet_transactions
ORDER BY created_at DESC LIMIT 20;

-- Check applications
SELECT a.id, j.title, a.is_accepted, a.created_at
FROM applications a
JOIN jobs j ON j.id = a.job_id;
```

### Frontend — Debug Prints

Add these temporarily to trace issues:

```dart
// In AuthInterceptor — see what token is being sent
print('Token: ${session?.accessToken.substring(0, 20)}...');

// In any provider — see raw API response
print('Response: ${response.data}');

// In _ApplyButtonState — see exact error
} on DioException catch (e) {
  print('Status: ${e.response?.statusCode}');
  print('Data:   ${e.response?.data}');
}
```

---

## 11. Deployment

### Backend (Production)

```bash
# Install production dependencies
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# Or with Docker
docker build -t hustle-backend .
docker run -p 8000:8000 --env-file .env hustle-backend
```

**Production checklist:**
- [ ] Set `API_BASE_URL` to your real domain (not ngrok)
- [ ] Update Squad dashboard webhook URL to production URL
- [ ] Re-enable webhook signature verification in `webhook.py`
- [ ] Set up SSL/TLS (Squad requires HTTPS for webhooks)
- [ ] Switch Squad from sandbox to live keys

### Frontend (Production Build)

```bash
# iOS — creates .ipa for App Store
flutter build ipa --release

# Android — creates .aab for Play Store
flutter build appbundle --release

# Android APK (for direct distribution)
flutter build apk --release --split-per-abi
```

---

## 12. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `404` on `/api/v1/profile/worker` | Worker profile row doesn't exist | Call `POST /api/v1/auth/role {"role": "worker"}` |
| `400` on role select screen | User already has a role | Check `GET /api/v1/auth/me` for current role |
| `403` on apply button | User is not a worker | Set role to worker via auth endpoint |
| `403` on wallet top-up | User is not an employer | Only employers can top up; workers earn via escrow |
| Squad returns `403` | API key expired or invalid | Get a fresh key from sandbox.squadco.com → Settings |
| Squad returns `500` | Squad sandbox is down | Wait and retry; try direct curl to confirm |
| Map shows wrong location | Emulator has no GPS | Set Lagos coordinates in Simulator/Emulator settings |
| `column X does not exist` | SQLAlchemy model out of sync with DB | Check actual columns with Supabase SQL Editor and update the model |
| `duplicate key value` on login | Same email, different UUID in Supabase | `get_or_create_user` fallback handles this; check `auth_service.py` |
| Webhook not firing | ngrok not running or wrong URL | Ensure ngrok is active and URL in Squad dashboard is updated |
| Flutter polling never fires | `_previousBalance` wrong | Print balance before and after to confirm values differ |
| `skills` column type mismatch | Model uses JSON instead of `ARRAY(Text)` | Use `mapped_column(ARRAY(Text))` from `sqlalchemy.dialects.postgresql` |

---

## Key Decisions & Trade-offs

| Decision | Reason |
|---|---|
| **Squad VA over card payments** | Nigerian workers have bank accounts, not cards. VA works with any bank transfer |
| **Escrow in DB, not Squad** | Squad doesn't offer native escrow; we implement it as a wallet state machine |
| **Kobo for all money values** | Avoids floating-point errors in financial calculations |
| **ES256 JWT verified at startup** | Caching the public key avoids 2500ms latency per request |
| **Worker role blocks wallet top-up** | Workers earn via escrow only; top-up is employer-only by design |
| **OSM instead of Google Maps** | No billing, no API key friction, works offline with caching |
| **Riverpod over BLoC** | Less boilerplate, better async support, easier testing |
| **NullPool for DB connections** | Required for Supabase's connection pooler (pgBouncer in transaction mode) |

---

*Built for the Hackathon · Solving the Informal Labour Crisis in Nigeria*

*HUSTLE — designed to become a GTBank subsidiary, leveraging GTBank's banking licence for regulated escrow at national scale.*
