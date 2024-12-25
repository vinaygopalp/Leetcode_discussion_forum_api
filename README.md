# Leetcode CLone

just tried to clone Leetcode functionalties 
---

## Features

- **Feature 1:** WebSocket connection.
- **Feature 2:** REST API for data fetching and management.
- **Feature 3:** JWT-based authentication with endpoints for login, registration, and token refresh.

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

#### **Authentication**

##### **Login**
- **Endpoint:** `http://127.0.0.1:8000/auth/login/`  
  - **Method:** POST
  - **Purpose:** Authenticate a user and retrieve access/refresh tokens.
  - **Sample Request:**
    ```json
    {
        "username": "fuckkk",
        "password": "123",
        "roles": "admin,user"
    }
    ```
  - **Sample Response:**
    ```json
    {
        "refresh": "<refresh_token>",
        "access": "<access_token>"
    }
    ```

##### **Token Pair**
- **Endpoint:** `http://127.0.0.1:8000/auth/api/token/`  
  - **Method:** POST
  - **Purpose:** Obtain a new access and refresh token pair.
  - **Sample Request:**
    ```json
    {
        "username": "vinay",
        "password": "123",
        "roles": "admin,user"
    }
    ```

##### **Token Refresh**
- **Endpoint:** `http://127.0.0.1:8000/auth/api/token/refresh/`  
  - **Method:** POST
  - **Purpose:** Refresh the access token using the refresh token.
  - **Sample Request:**
    ```json
    {
        "refresh": "<refresh_token>"
    }
    ```

##### **Register**
- **Endpoint:** `http://127.0.0.1:8000/auth/register/`  
  - **Method:** POST
  - **Purpose:** Register a new user.
  - **Sample Request:**
    ```json
    {
        "username": "fuckkk",
        "password": "123",
        "roles": "admin,user"
    }
    ```
  - **Sample Response:**
    ```json
    {
        "status": "User created"
    }
    ```

---

## Installation

### **Option 1: Using Docker (Recommended)**

#### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
