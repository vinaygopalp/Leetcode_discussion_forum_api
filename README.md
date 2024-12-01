# Project Name

A brief description of your project, including its purpose and key functionalities.

---

## Features

- **Feature 1:** websocket connection
- **Feature 2:** RESTAPI for fetching.


---

## Prerequisites

Ensure you have the following installed:

- **Python 3.x**
- **Docker** (for containerized deployment)
- **pip** (ensure it's updated: `pip install --upgrade pip`)

---
## ENDPOINTS
- **http://127.0.0.1:8000/chat/<chatroom_name>/  (for websocket connecting )
# json format {"message": message,  "sender":sender}


- **http://127.0.0.1:8000/message_api/room/  (restapi for get,put,delete room)

# json format 
    {
        "id": 1,
        "created_at": "2024-11-30T18:10:33.187438Z",
        "room": "probel1"
    }

- **http://127.0.0.1:8000/message_api/user/ (restapi for get,post,delete user)
# json format 
[
    {
        "id": 1,
        "user_name": "vinay"
    }
]


- **http://127.0.0.1:8000/message_api/message/  (restapi for get,posting,deleting messages)
# format [
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
        "content": "fuck",
        "timestamp": "2024-11-30T18:11:25.156366Z"
    },
   
]


## Installation

### **Option 1: Using Docker (Recommended)**

#### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
