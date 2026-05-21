# SOUL-LMS Quick Start Guide

## 🚀 Get Running in 5 Minutes

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Start Backend (Terminal 1)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

✅ Backend running at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

✅ Frontend running at `http://localhost:5173`

### 4. Test a Complete Flow

**Step 1: Get Auth Token**
```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=stud@lms.com&password=stud123"
```

Note the `access_token` from response.

**Step 2: Create an Alert Rule**
```bash
TOKEN="your-token-here"

curl -X POST http://localhost:8000/api/alerts/rules \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 1,
    "alert_type": "FATIGUE",
    "trigger_metric": "fatigue_score",
    "threshold": 5,
    "operator": ">=",
    "severity": "HIGH"
  }'
```

**Step 3: Check Alerts**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/alerts/student/1
```

**Step 4: View in Frontend**
- Open http://localhost:5173
- Navigate to "Alerts" page
- Alerts should appear!

---

## 📊 New Features Overview

### 1. **Alert System** 🔔
- **What:** Automatically detects student problems (fatigue, low performance, etc.)
- **Where:** `/alerts` page
- **API:** `POST /api/alerts/rules`, `GET /api/alerts/student/{id}`

### 2. **Remedial Modules** 📚
- **What:** Personalized learning content generated based on skill gaps
- **Where:** `/remediation` page
- **API:** `POST /api/remediation/modules`, `GET /api/remediation/student/{id}/{course}`

### 3. **Reflection Journal** 📝
- **What:** Prompts for student self-reflection and learning improvement
- **Where:** `/reflection` page
- **API:** `POST /api/reflection/prompts`, `POST /api/reflection/prompts/{id}/submit`

### 4. **Ethics Tracking** ⚖️
- **What:** Monitor student academic integrity and responsibility
- **Where:** `/ethics` page
- **API:** `GET /api/ethics/profile/{id}`, `POST /api/ethics/flag/{id}`

### 5. **Adaptive Curriculum** 🎯
- **What:** AI-powered course sequencing based on student needs
- **Where:** Behind the scenes, triggered by alerts
- **API:** `POST /api/curriculum/analyze/{sid}/{cid}`

### 6. **Real-Time Engagement** 📈
- **What:** Live tracking of student engagement metrics
- **Where:** `/engagement` page
- **API:** `GET /api/engagement/snapshots/{sid}/{cid}`

---

## 🧪 Quick Test Data

The system automatically creates test users on startup:

```
ADMIN:
  Email: admin@lms.com
  Password: admin123
  Role: ADMIN

INSTRUCTOR:
  Email: instr@lms.com
  Password: instr123
  Role: INSTRUCTOR

STUDENT:
  Email: stud@lms.com
  Password: stud123
  Role: STUDENT
```

Login with any of these credentials on the frontend.

---

## 🔄 System Architecture

```
┌─────────────────────────────────────┐
│         Frontend (React)             │
│    http://localhost:5173             │
│  - Alerts, Remediation, etc.        │
└────────────┬────────────────────────┘
             │ API Calls
             ↓
┌─────────────────────────────────────┐
│       Backend (FastAPI)              │
│    http://localhost:8000/docs        │
│ - 30+ REST endpoints                │
│ - Alert management                  │
│ - Content generation (LLM)          │
│ - Scheduler (background jobs)       │
└────────────┬────────────────────────┘
             │ Read/Write
             ↓
┌─────────────────────────────────────┐
│   Database (SQLite)                 │
│    ./lms.db                          │
│  - Users, Courses, Assignments      │
│  - Alerts, Remediation Modules      │
│  - Ethics Profiles, Engagement      │
└─────────────────────────────────────┘
```

---

## 🎯 What Each Page Does

### 1. Alerts (`/alerts`)
- Shows all active alerts for student
- Severity badges (HIGH, MEDIUM, LOW)
- Dismiss/Acknowledge functionality
- Auto-refreshes every 30 seconds

### 2. Remediation Dashboard (`/remediation`)
- Browse available learning modules
- Filter by difficulty level
- View content (text, video, etc.)
- Track completion percentage
- See remediation recommendations

### 3. Reflection Journal (`/reflection`)
- View context-based reflection prompts
- Submit written responses
- AI analyzes reflection quality
- Sentiment analysis of responses
- Track reflection history

### 4. Ethics Tracking (`/ethics`)
- View ethical profile scorecard
- 4 metrics: Integrity, Collaboration, Self-Regulation, Responsibility
- Violation flags and history
- Best practices guide
- Improvement suggestions

### 5. Real-Time Engagement (`/engagement`)
- Current engagement score (0-100)
- Activity count tracker
- 24-hour activity timeline
- 7-day trend chart
- Auto-updates every 60 seconds

---

## 🛠️ Common Operations

### Create an Alert Rule
```bash
POST /api/alerts/rules
{
  "student_id": 1,
  "course_id": 1,
  "alert_type": "FATIGUE",
  "trigger_metric": "fatigue_score",
  "threshold": 5,
  "operator": ">=",
  "severity": "HIGH"
}
```

### Manually Trigger Alert Check
```bash
POST /api/alerts/check/{student_id}/{course_id}
```

### Create Remediation Module
```bash
POST /api/remediation/modules
{
  "student_id": 1,
  "course_id": 1,
  "title": "Quadratic Equations",
  "skill_gap": "Quadratic Equations",
  "difficulty_level": "INTERMEDIATE",
  "content": "...",
  "content_type": "TEXT"
}
```

### Trigger Adaptive Curriculum
```bash
POST /api/curriculum/analyze/1/1
{
  "current_modules": [1, 2, 3]
}
```

### Create Engagement Snapshot
```bash
POST /api/engagement/snapshot
{
  "student_id": 1,
  "course_id": 1,
  "engagement_score": 75,
  "activity_count": 12,
  "avg_response_time": 2.5,
  "trend": "INCREASING"
}
```

---

## 🔍 Debugging

### Check Backend Logs
```bash
# Terminal where backend is running - watch for:
# - "Alert created for student..."
# - "Scheduler started"
# - "Alert check job running"
```

### Check API Docs
```
http://localhost:8000/docs
```
- Try all endpoints here
- See response examples
- Debug request parameters

### Check Database
```bash
# View tables in SQLite
sqlite3 backend/lms.db

# List all tables
.tables

# Check alerts
SELECT * FROM student_alerts;

# Check modules
SELECT * FROM remediation_modules;
```

### Clear Database (Reset)
```bash
rm backend/lms.db
# Restart backend - will recreate with test data
```

---

## 📈 Production Checklist

- [ ] Update database URL (PostgreSQL instead of SQLite)
- [ ] Set OpenAI API key for LLM features
- [ ] Configure JWT secret key
- [ ] Enable CORS for your domain
- [ ] Set up email notifications
- [ ] Enable WebSocket for real-time updates
- [ ] Add unit tests
- [ ] Deploy backend (Heroku, AWS, etc.)
- [ ] Deploy frontend (Vercel, Netlify, etc.)
- [ ] Monitor with logging/alerts
- [ ] Set up database backups

---

## 📞 Support

**If something breaks:**
1. Check console for error messages
2. Verify backend is running (`curl http://localhost:8000/docs`)
3. Verify frontend can reach backend
4. Check database exists (`ls backend/lms.db`)
5. Reset database if needed (`rm backend/lms.db`)
6. Check logs in terminal where backend is running

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then kill process |
| Database locked | Delete `lms.db` and restart |
| CORS errors | Check backend CORS settings |
| 401 Unauthorized | Token expired, login again |
| API returns 500 | Check backend terminal for error |

---

**Happy Learning! 🚀**

For detailed implementation info, see `IMPLEMENTATION_COMPLETE.md`
