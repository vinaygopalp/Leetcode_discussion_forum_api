# Project Name

A brief description of your project, including its purpose and key functionalities.

---

## Features

- **Feature 1:** WebSocket connection.
- **Feature 2:** REST API for data fetching and management.

---

## Prerequisites

Ensure you have the following installed:

- **Python 3.x**
- **Docker** (for containerized deployment)
- **pip** (ensure it's updated: `pip install --upgrade pip`)

---

## Endpoints

### **WebSocket Connection**
- **Endpoint:** `ws://127.0.0.1:8000/chat/<chatroom_name>/`  
  - **Purpose:** Establish a WebSocket connection for live chat.
  - **Sample JSON Message:**
    ```json
    {
        "message": "Hello, World!",
        "sender": "user_name"
    }
    ```

---

### **REST APIs**

#### **Room Management**
- **Endpoint:** `http://127.0.0.1:8000/message_api/room/`  
  - **Methods:** GET, PUT, DELETE
  - **Purpose:** Manage chat rooms.
  - **Sample JSON Response:**
    ```json
    [
        {
            "id": 1,
            "created_at": "2024-11-30T18:10:33.187438Z",
            "room": "room_name"
        }
    ]
    ```

---

#### **User Management**
- **Endpoint:** `http://127.0.0.1:8000/message_api/user/`  
  - **Methods:** GET, POST, DELETE
  - **Purpose:** Manage users.
  - **Sample JSON Response:**
    ```json
    [
        {
            "id": 1,
            "user_name": "vinay"
        }
    ]
    ```

---

#### **Message Management**
- **Endpoint:** `http://127.0.0.1:8000/message_api/message/`  
  - **Methods:** GET, POST, DELETE
  - **Purpose:** Manage chat messages.
  - **Sample JSON Response:**
    ```json
    [
        {
            "id": 1,
            "user_name": {
                "id": 1,
                "user_name": "vinay"
            },
            "room": {
                "id": 4,
                "created_at": "2024-11-30T18:10:55.289960Z",
                "room": "problem2"
            },
            "content": "Hello!",
            "timestamp": "2024-11-30T18:11:25.156366Z"
        }
    ]
    ```

---

## Installation

### **Option 1: Using Docker (Recommended)**

#### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
