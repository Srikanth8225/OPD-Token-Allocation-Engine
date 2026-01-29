# OPD Token Allocation Engine

A production-ready backend service for managing outpatient department (OPD) token allocation with dynamic reallocation, priority handling, and real-world edge case management.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Algorithm Details](#algorithm-details)
- [Simulation](#simulation)
- [Project Structure](#project-structure)

## 🎯 Overview

The OPD Token Allocation Engine is a REST API-based service that intelligently allocates patient tokens across doctors and time slots while handling:

- **Capacity Management**: Hard limits per time slot
- **Priority-based Allocation**: 5-tier priority system
- **Dynamic Reallocation**: Automatic waitlist promotion on cancellations/no-shows
- **Emergency Handling**: Highest priority with cascading demotion
- **Multiple Sources**: Online booking, walk-in, paid priority, follow-up, emergency

## ✨ Features

### Core Features

- ✅ **Token Allocation** with priority-based queuing
- ✅ **Dynamic Reallocation** on state changes
- ✅ **Emergency Insertion** with smart demotion
- ✅ **Waitlist Management** with automatic promotion
- ✅ **Capacity Enforcement** (no overbooking)
- ✅ **Multi-source Support** (5 token sources)
- ✅ **Real-time Status** tracking per slot
- ✅ **Estimated Wait Times** calculation

### Priority Levels (Highest → Lowest)

1. **EMERGENCY** (Priority 1) - Critical cases
2. **PAID_PRIORITY** (Priority 2) - VIP/Premium patients
3. **FOLLOW_UP** (Priority 3) - Return consultations
4. **ONLINE_BOOKING** (Priority 4) - Pre-booked appointments
5. **WALK_IN** (Priority 5) - OPD desk registrations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      REST API Layer                          │
│         (Flask Routes - Validation & Formatting)             │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                      Service Layer                           │
│    (AllocationService, ReallocationService)                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                      Core Engine                             │
│     (PriorityManager, QueueManager)                          │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                      Data Models                             │
│   (Doctor, TimeSlot, Token, Patient)                         │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

- **API Layer**: Request validation, response formatting, HTTP handling
- **Service Layer**: Business logic, allocation/reallocation algorithms
- **Core Engine**: Priority management, queue sorting, waitlist operations
- **Data Models**: Entity definitions, state management, relationships

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# Clone or navigate to project directory
cd opd-token-engine

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

The API will be available at `http://localhost:5000/api`

## 📖 Usage

### Starting the Server

```bash
python run.py
```

### Running the Simulation

```bash
python simulation/opd_day_simulation.py
```

This simulates a full OPD day with 3 doctors, multiple slots, and various scenarios.

## 🔌 API Documentation

### Base URL

```
http://localhost:5000/api
```

### Endpoints

#### 1. Create Doctor

```http
POST /api/doctors
Content-Type: application/json

{
  "name": "Dr. Rajesh Kumar",
  "specialization": "Cardiology",
  "doctor_id": "DOC001"
}
```

#### 2. Create Time Slots

```http
POST /api/doctors/{doctor_id}/slots
Content-Type: application/json

{
  "start_time": "09:00",
  "end_time": "10:00",
  "date": "2026-01-29",
  "max_capacity": 10
}
```

Or create multiple slots:

```http
POST /api/doctors/{doctor_id}/slots
Content-Type: application/json

[
  {
    "start_time": "09:00",
    "end_time": "10:00",
    "date": "2026-01-29",
    "max_capacity": 10
  },
  {
    "start_time": "10:00",
    "end_time": "11:00",
    "date": "2026-01-29",
    "max_capacity": 10
  }
]
```

#### 3. Allocate Token

```http
POST /api/tokens/allocate
Content-Type: application/json

{
  "patient": {
    "name": "Ramesh Singh",
    "phone": "9876543210",
    "age": 45,
    "gender": "M"
  },
  "doctor_id": "DOC001",
  "date": "2026-01-29",
  "preferred_slot_time": "09:00",
  "source": "ONLINE_BOOKING"
}
```

**Response (Confirmed)**:
```json
{
  "success": true,
  "data": {
    "token_id": "TKN20260129...",
    "token_number": 5,
    "status": "CONFIRMED",
    "patient_name": "Ramesh Singh",
    "doctor_name": "Dr. Rajesh Kumar",
    "slot_time": "09:00 - 10:00",
    "date": "2026-01-29",
    "estimated_time": "09:20",
    "source": "ONLINE_BOOKING",
    "priority": 4
  },
  "message": "CONFIRMED"
}
```

**Response (Waitlisted)**:
```json
{
  "success": true,
  "data": {
    "token_id": "TKN20260129...",
    "status": "WAITLISTED",
    "waitlist_position": 3,
    "estimated_wait": "15 minutes"
  },
  "message": "WAITLISTED (Position: 3)"
}
```

#### 4. Allocate Emergency Token

```http
POST /api/tokens/emergency
Content-Type: application/json

{
  "patient": {
    "name": "Emergency Patient",
    "phone": "9876543227",
    "age": 58,
    "gender": "M"
  },
  "doctor_id": "DOC001",
  "date": "2026-01-29",
  "preferred_slot_time": "09:00"
}
```

#### 5. Cancel Token

```http
POST /api/tokens/{token_id}/cancel
```

#### 6. Mark No-Show

```http
POST /api/tokens/{token_id}/no-show
```

#### 7. Get Slot Status

```http
GET /api/slots/{slot_id}/status
```

**Response**:
```json
{
  "success": true,
  "data": {
    "slot_id": "SLOT001",
    "doctor_name": "Dr. Rajesh Kumar",
    "time": "09:00 - 10:00",
    "date": "2026-01-29",
    "max_capacity": 10,
    "allocated": 8,
    "available": 2,
    "waitlist_count": 5,
    "confirmed_tokens": [...],
    "waitlisted_tokens": [...]
  }
}
```

#### 8. Get Token Details

```http
GET /api/tokens/{token_id}
```

#### 9. Get System Stats

```http
GET /api/stats
```

#### 10. Health Check

```http
GET /api/health
```

## 🧮 Algorithm Details

### Token Allocation Algorithm

**Step-by-step Process:**

1. **Validate Request**
   - Check doctor exists
   - Check slot exists
   - Validate source type

2. **Determine Priority**
   - Map source to priority level (1-5)
   - Lower number = higher priority

3. **Find Slot Capacity**
   - If slot has space → Allocate directly (CONFIRMED)
   - If slot is full → Add to waitlist (WAITLISTED)

4. **Assign Token Number**
   - Sequential within slot
   - Calculate estimated time

5. **Return Token**
   - Token ID, status, queue position

### Dynamic Reallocation Algorithm

**Triggered by**: Cancellation, No-Show, Emergency Insertion

**On Cancellation/No-Show:**

1. Mark token as CANCELLED/NO_SHOW
2. Free slot capacity
3. Check waitlist for same slot
4. Promote highest priority waitlisted token
5. Update: WAITLISTED → CONFIRMED
6. Assign token number and estimated time

**On Emergency Insertion:**

1. If slot has capacity → Allocate directly
2. If slot is full:
   - Find lowest priority confirmed token
   - Compare priorities
   - If emergency > lowest → Demote lowest, insert emergency
   - Else → Add emergency to waitlist

**Waitlist Promotion Logic:**

- Sort by: Priority (ascending), then Timestamp (FIFO)
- Promote top candidate
- Update token status and details

### Edge Cases Handled

1. ✅ **Overbooking Prevention**: Hard capacity check
2. ✅ **Empty Waitlist**: No promotion, capacity remains free
3. ✅ **All Slots Full**: Waitlist with position tracking
4. ✅ **Emergency During Full Day**: Cascading demotion
5. ✅ **Multiple Cancellations**: Sequential processing
6. ✅ **Concurrent Requests**: Atomic slot operations
7. ✅ **Invalid Requests**: Proper error handling

## 🎭 Simulation

The simulation demonstrates a complete OPD day with:

- **3 Doctors** (Cardiology, Orthopedics, General Medicine)
- **4 Slots per Doctor** (9-10, 10-11, 11-12, 12-1)
- **Various Capacities** (8-10 patients per slot)

### Simulation Phases

1. **Setup** - Create doctors and slots
2. **Morning Rush** - Online bookings (10 patients)
3. **Walk-ins** - OPD desk registrations (5 patients)
4. **Paid Priority** - VIP bookings (2 patients)
5. **Cancellations** - Some patients cancel (3 tokens)
6. **Emergency** - Critical insertions (2 patients)
7. **No-Shows** - Patients don't arrive (2 tokens)
8. **Follow-ups** - Return consultations (2 patients)

### Expected Output

- Event timeline with timestamps
- Token allocation details
- Cancellation and promotion events
- Final utilization statistics
- Per-doctor capacity analysis
- Constraint validation

## 📁 Project Structure

```
opd-token-engine/
├── app/
│   ├── __init__.py               # Flask app factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patient.py            # Patient model
│   │   ├── doctor.py             # Doctor model
│   │   ├── time_slot.py          # TimeSlot model
│   │   └── token.py              # Token model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── allocation_service.py # Token allocation logic
│   │   └── reallocation_service.py # Reallocation logic
│   ├── core/
│   │   ├── __init__.py
│   │   ├── priority_manager.py   # Priority handling
│   │   └── queue_manager.py      # Waitlist management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py             # REST API endpoints
│   └── utils/
│       ├── __init__.py
│       └── data_store.py         # In-memory data store
├── simulation/
│   ├── __init__.py
│   └── opd_day_simulation.py     # Full day simulation
├── tests/                        # (Future: unit tests)
├── config.py                     # Configuration
├── run.py                        # Server entry point
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## ⚖️ Trade-offs and Assumptions

### Trade-offs

1. **Fairness vs. Urgency**
   - **Decision**: Priority-based (urgency wins)
   - **Impact**: Lower priority patients may wait longer
   - **Mitigation**: Transparent waitlist positions, estimated times

2. **Cascading Demotion vs. Rejection**
   - **Decision**: Demote lower priority for emergencies
   - **Impact**: Inconvenience to demoted patients
   - **Mitigation**: Immediate notification, auto re-booking

3. **In-Memory vs. Database**
   - **Decision**: In-memory for this implementation
   - **Impact**: Data lost on restart
   - **Future**: Migrate to PostgreSQL/MongoDB

4. **Synchronous vs. Asynchronous**
   - **Decision**: Synchronous reallocation
   - **Impact**: Slight latency on cancellation
   - **Benefit**: Immediate consistency

### Assumptions

1. Single-day scope (no multi-day scheduling)
2. Fixed 1-hour slot duration (configurable)
3. Sequential token numbers within slots
4. 15-minute grace period before no-show
5. EMERGENCY source = highest priority
6. Waitlist auto-accept on promotion
7. No partial consultations

## 🔮 Future Improvements

1. **Database Integration**: PostgreSQL with migrations
2. **Real-time Notifications**: WebSocket/SMS alerts
3. **Analytics Dashboard**: Grafana/Custom UI
4. **Machine Learning**: No-show prediction, capacity optimization
5. **Multi-facility Support**: Scale across hospitals
6. **Doctor Preferences**: Custom schedules, break times
7. **Patient History**: Consultation tracking
8. **Queue Display**: Digital signage for waiting area
9. **Appointment Reminders**: Automated notifications
10. **Authentication & Authorization**: Secure API access

## 📜 License

This project is for educational and demonstration purposes.

## 👨‍💻 Author

Senior Backend Engineer & System Designer

---

**Status**: Production-Ready MVP ✅  
**Last Updated**: 2026-01-29
