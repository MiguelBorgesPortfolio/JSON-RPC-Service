# JSON-RPC Service  

## 📌 About the Project  
This project implements a **JSON-RPC 2.0 remote procedure call (RPC) service**, enabling a client-server architecture where remote functions can be invoked over a network.  
The system consists of a **server** that exposes a set of functions and a **client** that interacts with the server via JSON-RPC requests.  

---

## 🛠 Technologies Used  
- **Python**  
- **Sockets (TCP/IP Communication)**  
- **JSON-RPC 2.0 Protocol**  
- **Multithreading for Parallel Clients**  
- **Unit Testing (unittest library)**  

---

## 📂 Project Structure  

### **1️⃣ Server**  
✔ Receives and processes **JSON-RPC requests**  
✔ Executes **registered functions** and returns results  
✔ Handles **error validation and incorrect requests**  
✔ Supports **multiple simultaneous client connections**  

### **2️⃣ Client**  
✔ Connects to the server and sends **JSON-RPC requests**  
✔ Dynamically invokes **remote functions**  
✔ Handles **responses and errors gracefully**  

### **3️⃣ Unit Testing**  
✔ `tests_server.py` → Validates **server request handling and response formatting**  
✔ `tests_client.py` → Ensures **client correctly sends and processes JSON-RPC requests**  

---

