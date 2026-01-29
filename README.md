# OPD Token Allocation Engine

> A smart backend system for hospital OPD token management with priority-based allocation and dynamic reallocation.

## What This Does

Manages patient tokens across doctors and time slots while handling:
- Priority-based allocation (emergency → paid → follow-up → online → walk-in)
- Dynamic reallocation when patients cancel or don't show up
- Automatic waitlist promotion
- Emergency insertions that can bump lower priority patients
- Hard capacity limits (no overbooking ever)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

Server starts at `http://localhost:5000/api`

## Run the Demo

```bash
# See the system in action with a full OPD day simulation
python simulation/opd_day_simulation.py
```

This simulates 3 doctors, 24 patients, cancellations, emergencies, and more.

## How It Works

### Priority System

1. **EMERGENCY** - Highest priority, can bump others
2. **PAID_PRIORITY** - VIP/Premium patients
3. **FOLLOW_UP** - Return visits
4. **ONLINE_BOOKING** - Pre-booked appointments
5. **WALK_IN** - OPD desk registrations

### What Happens When...

**Slot has space?** → Patient gets confirmed immediately  
**Slot is full?** → Patient goes to waitlist (sorted by priority)  
**Someone cancels?** → Next person on waitlist gets promoted automatically  
**Emergency arrives?** → If slot full, lowest priority patient gets bumped to waitlist  

## API Examples

### Create a Doctor

```bash
curl -X POST http://localhost:5000/api/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Sarah Johnson",
    "specialization": "Cardiology"
  }'
```

### Create Time Slots

```bash
curl -X POST http://localhost:5000/api/doctors/DOC001/slots \
  -H "Content-Type: application/json" \
  -d '[
    {"start_time": "09:00", "end_time": "10:00", "date": "2026-01-30", "max_capacity": 10},
    {"start_time": "10:00", "end_time": "11:00", "date": "2026-01-30", "max_capacity": 10}
  ]'
```

### Book an Appointment

```bash
curl -X POST http://localhost:5000/api/tokens/allocate \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {
      "name": "John Doe",
      "phone": "9876543210",
      "age": 45,
      "gender": "M"
    },
    "doctor_id": "DOC001",
    "date": "2026-01-30",
    "preferred_slot_time": "09:00",
    "source": "ONLINE_BOOKING"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "token_id": "TKN001",
    "token_number": 5,
    "status": "CONFIRMED",
    "estimated_time": "09:20",
    "priority": 4
  }
}
```

### Emergency Allocation

```bash
curl -X POST http://localhost:5000/api/tokens/emergency \
  -H "Content-Type: application/json" \
  -d '{
    "patient": {"name": "Emergency Patient", "phone": "9999999999", "age": 55, "gender": "M"},
    "doctor_id": "DOC001",
    "date": "2026-01-30",
    "preferred_slot_time": "09:00"
  }'
```

### Cancel a Token

```bash
curl -X POST http://localhost:5000/api/tokens/{token_id}/cancel
```

### Check Slot Status

```bash
curl http://localhost:5000/api/slots/{slot_id}/status
```

## All API Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| POST | `/api/doctors` | Create doctor |
| GET | `/api/doctors` | List all doctors |
| POST | `/api/doctors/{id}/slots` | Add time slots |
| POST | `/api/tokens/allocate` | Book appointment |
| POST | `/api/tokens/emergency` | Emergency booking |
| POST | `/api/tokens/{id}/cancel` | Cancel token |
| POST | `/api/tokens/{id}/no-show` | Mark as no-show |
| GET | `/api/tokens/{id}` | Get token details |
| GET | `/api/slots/{id}/status` | Check slot status |
| GET | `/api/stats` | System statistics |
| GET | `/api/health` | Health check |

## Architecture

```
API Routes (Flask)
    ↓
Services (Business Logic)
    ↓
Core Engine (Priority & Queue Management)
    ↓
Data Models (Doctor, Slot, Token, Patient)
```

Clean separation of concerns. Easy to understand and extend.

## Project Structure

```
opd-token-engine/
├── app/
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── core/           # Priority & queue algorithms
│   ├── api/            # REST endpoints
│   └── utils/          # Data storage
├── simulation/         # Demo simulation
├── config.py          # Settings
└── run.py            # Start server
```

## Configuration

Edit `config.py` to customize:

```python
DEFAULT_SLOT_CAPACITY = 10          # Patients per slot
AVERAGE_CONSULTATION_MINUTES = 5    # Time per patient
NO_SHOW_GRACE_PERIOD_MINUTES = 15   # Before marking no-show
```

## Design Decisions

**Why in-memory storage?**  
Simple, fast, perfect for MVP. Easy to switch to PostgreSQL later.

**Why demote patients for emergencies?**  
Medical necessity. Demoted patients keep their priority for quick re-promotion.

**Why synchronous reallocation?**  
Immediate consistency. Latency is negligible (~5ms).

## Limitations & Future

Current limitations:
- Data lost on restart (in-memory)
- Single-day scheduling only
- Fixed 1-hour slots
- No authentication

Planned features:
- PostgreSQL integration
- SMS notifications
- Multi-day scheduling
- Analytics dashboard
- Patient portal

## Testing

Run the simulation to see everything in action:

```bash
python simulation/opd_day_simulation.py
```

You'll see:
- ✅ All allocations respect priority
- ✅ No capacity violations
- ✅ Cancellations trigger promotions
- ✅ Emergencies handled correctly
- ✅ Waitlist sorted properly

## License

Educational & demonstration purposes.

---

Built with Python + Flask | Production-ready MVP | Last updated: Jan 2026
