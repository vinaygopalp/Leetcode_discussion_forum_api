```markdown
# Leetcode Clone

Just tried to clone some Leetcode functionalities.
---

## Features

- **Feature 1:** WebSocket-based real-time chat.
- **Feature 2:** REST API for managing contests, messages, rooms, and users.
- **Feature 3:** JWT-based authentication (login, register, refresh token).

---

## Prerequisites

Ensure you have the following installed:

- **Python 3.x**
- **Docker** (for containerized deployment)
- **pip** (upgrade it: `pip install --upgrade pip`)

---

## Endpoints

### **WebSocket Connection**
- **URL:** `ws://127.0.0.1:8000/ws/chat/<problem_id>/`
- **Purpose:** Real-time chat based on problem id.

**Sample WebSocket Message:**
```json
{
  "message": "Hello World!",
  "sender": "user123"
}
```

---

### **REST APIs**

#### **Contest Management**

- **POST** `/message_api/contest_template/`  
  Create a new contest template.

**Sample Request:**
```json
{
  "title": "Weekly Contest 1",
  "description": "First contest description"
}
```

- **POST** `/message_api/schedule_contest/`  
  Schedule a contest.

**Sample Request:**
```json
{
  "title": "Weekly Contest 1",
  "start_time": "2025-04-06T10:00:00Z",
  "end_time": "2025-04-06T12:00:00Z"
}
```

- **POST** `/message_api/contest_start/`  
  Start a contest immediately.

**Sample Request:**
```json
{
  "title": "Weekly Contest 1"
}
```

- **GET** `/message_api/all_templates/`  
  Fetch all contest templates.

**Sample Response:**
```json
[
  {
    "id": 1,
    "title": "Weekly Contest 1",
    "description": "First contest description"
  }
]
```

- **GET** `/message_api/all_schedules/`  
  Fetch all scheduled contests.

**Sample Response:**
```json
[
  {
    "id": 1,
    "title": "Weekly Contest 1",
    "start_time": "2025-04-06T10:00:00Z",
    "end_time": "2025-04-06T12:00:00Z"
  }
]
```

- **DELETE** `/message_api/delete_all_contests/`  
  Delete all scheduled contests.

- **DELETE** `/message_api/delete_all_templates/`  
  Delete all contest templates.

---

#### **Room Management**

- **POST** `/message_api/room/`  
  Create a chat room.

**Sample Request:**
```json
{
  "room": "problem_123"
}
```

- **GET** `/message_api/room/`  
  Fetch all rooms.

**Sample Response:**
```json
[
  {
    "id": 1,
    "room": "problem_123",
    "created_at": "2025-04-06T09:00:00Z"
  }
]
```

- **DELETE** `/message_api/room/`  
  Delete a chat room.

---

#### **User Management**

- **POST** `/message_api/user/`  
  Add a user.

**Sample Request:**
```json
{
  "user_name": "vinay"
}
```

- **GET** `/message_api/user/`  
  Fetch users.

**Sample Response:**
```json
[
  {
    "id": 1,
    "user_name": "vinay"
  }
]
```

- **DELETE** `/message_api/user/`  
  Delete a user.

---

#### **Message Management**

- **GET** `/message_api/message/`  
  Fetch messages from a room.

**Sample Response:**
```json
[
  {
    "id": 1,
    "user_name": {
      "id": 1,
      "user_name": "vinay"
    },
    "room": {
      "id": 2,
      "room": "problem_123"
    },
    "content": "Hello!",
    "timestamp": "2025-04-06T09:30:00Z"
  }
]
```

---

#### **Code Complexity Analysis**

- **POST** `/message_api/comp/`  
  Analyze code complexity.

**Sample Request:**
```json
{
  "code": "def add(a, b): return a + b"
}
```

**Sample Response:**
```json
{
  "complexity": "O(1)"
}
```

---

### **Authentication**

#### **Login**
- **POST** `/auth/login/`  
  Login and get JWT tokens.

**Sample Request:**
```json
{
  "username": "vinay",
  "password": "123",
  "roles": "admin,user"
}
```

**Sample Response:**
```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

---

#### **Register**
- **POST** `/auth/register/`  
  Register a new user.

**Sample Request:**
```json
{
  "username": "vinay",
  "password": "123",
  "roles": "admin,user"
}
```

**Sample Response:**
```json
{
  "status": "User created"
}
```

---

#### **Token Obtain**
- **POST** `/auth/api/token/`  
  Obtain a new token.

**Sample Request:**
```json
{
  "username": "vinay",
  "password": "123",
  "roles": "admin,user"
}
```

---

#### **Token Refresh**
- **POST** `/auth/api/token/refresh/`  
  Refresh access token.

**Sample Request:**
```json
{
  "refresh": "<refresh_token>"
}
```

---

## Installation

### **Option 1: Using Docker (Recommended)**

#### Step 1: Clone the Repository
```bash
git clone https://github.com/vinaygopalp/Leetcode_discussion_forum_api.git
 
```

#### Step 2: Build and Run with Docker
```bash
docker-compose up --build
```

---

### **Option 2: Manual Setup**

#### Step 1: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Run Migrations
```bash
python manage.py migrate
```

#### Step 4: Start Server
```bash
python manage.py runserver
```

---

## Notes

- Ensure RabbitMQ and Redis are running.
- WebSocket endpoints are secured with JWT tokens.
- Contest templates are managed using a Redis sorted set.

---
```
