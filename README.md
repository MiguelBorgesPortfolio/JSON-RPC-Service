# Tasklists API

## 📌 About the Project  
Tasklists is a **Software-as-a-Service (SaaS) application** for **project and task management**.  
This project includes a fully implemented **RESTful API** using Flask, allowing multiple frontends (web, mobile, etc.) to interact with the system.  

---

## 🛠 Technologies Used  
- **Python**  
- **Flask** (Python Web Framework)  
- **SQLite3** (Database)  

---

## 🌐 API Endpoints  
### **Users**  
- `POST /api/user/register/` → Register a new user  
- `GET/PUT /api/user/` → Retrieve or update user information  

### **Projects**  
- `GET/POST /api/projects/` → Retrieve a list of projects or add a new project  
- `GET/PUT/DELETE /api/projects/<id>/` → Retrieve, update, or delete a project  

### **Tasks**  
- `GET/POST /api/projects/<id>/tasks/` → Retrieve tasks or add a new task  
- `GET/PUT/DELETE /api/projects/<id>/tasks/<id>/` → Retrieve, update, or delete a task  

📝 **All API endpoints exchange data in JSON format.**  

---

## 🔑 Authentication  
This API uses **Basic Authentication** to protect endpoints (except user registration).  
- Users must provide valid credentials to access project and task data.  

---

## 🧪 Testing  
The project includes a `tests.py` file with **unit tests** to validate API functionality.  


 
