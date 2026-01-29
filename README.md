## Home Automation Switch using Raw Sockets

## Project Overview
The **Home Automation Switch using Raw Sockets** is a client–server based application designed to control and monitor household appliances over a network. The system provides a **Graphical User Interface (GUI)** for both the **server** and **client**, enabling real-time, synchronized control of appliances such as lights, fans, air conditioners, heaters, and more.

The application supports **multiple clients connecting simultaneously to a single server**, allowing different users to control appliances concurrently. Any action performed by one client is instantly reflected on the server and all other connected clients, ensuring consistent and real-time state synchronization across the system.

The server follows a **multi-threaded architecture**, where each connected client is handled independently. This allows multiple users to control appliances at the same time while the administrator can start or stop the server and manually control appliances from the server GUI.

---

## Key Features
- Multi-client support with a centralized server  
- Real-time appliance state synchronization  
- Graphical User Interface (GUI) for both client and server  
- Secure communication using SSL (Secure Socket Layer)  
- Encrypted transmission of commands and credentials  
- Appliance control from both server and client  
- Dynamic addition and removal of appliances  
- Timer-based and scheduled appliance control  
- Login authentication for clients  
- Multi-threaded server architecture  

---

## System Architecture
The system is based on a **client–server architecture** implemented using **raw TCP sockets**.

### Server:
- Accepts multiple SSL-encrypted client connections  
- Maintains appliance states and schedules  
- Broadcasts updates to all connected clients  
- Provides a GUI for manual appliance control  
- Handles timers and scheduled actions  

### Client:
- Connects securely to the server using SSL  
- Displays real-time appliance states  
- Allows users to control appliances via GUI  
- Supports scheduling and timers  
- Requires login authentication  

---

## Security Implementation (SSL)
To ensure secure communication, **SSL (Secure Socket Layer)** is implemented between the client and server.

### Security Features:
- Encrypted data transmission  
- Mutual authentication using certificates  
- Protection against eavesdropping and man-in-the-middle attacks  
- Secure exchange of login credentials and control commands  

All communication between the client and server is encrypted using SSL certificates.

---

## Technologies Used
- **Programming Language:** Python  
- **Networking:** Raw TCP Sockets  
- **Security:** SSL / TLS  
- **GUI Framework:** Tkinter  
- **Concurrency:** Multi-threading  

---

## How to Generate SSL Certificates

The project uses **self-signed SSL certificates** for secure communication.  
Follow the steps below to generate the required certificates.

### Step 1: Create a Certificate Authority (CA)
```bash
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 365 -out ca.crt
```
### Step 2: Generate Server Certificate
```bash
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256
```
### Step 3: Generate Client Certificate
```bash
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256
```
### Step 4: Place Certificates

Ensure the following files are placed in the correct directories:

Server Directory:
-server.crt
-server.key
-ca.crt

Client Directory:
-client.crt
-client.key
-ca.crt

## How to Run the Project

### Prerequisites
-Python 3.8 or above
-OpenSSL installed
-All SSL certificates generated and placed correctly

### Step 1: Start the Server
```bash
python server.py
```
### Step 2: Run the Client
```bash
python client.py
```




