# Developing A Deliberately Vulnerable Web Application (DVWA) For Insecure Direct Object Reference (IDOR) Vulnerability Education
This project is designed to teach and demonstrate Insecure Direct Object Reference (IDOR) vulnerabilities. It simulates a social media platform, created using the following features:
-  Django-based main web application
-  Separate Flask API exposing vulnerable endpoints
-  Docker for deployment
-  Five exercises based on real-world IDOR types (URL tampering, cookie manipulation, body manipulation, HTTP API manipulation, JSON API manipulation)
## Requirements
- Docker desktop
- Burp Suite Community Edition for intercepting requests
## Setup
- Clone the repository:
  - 'git clone https://github.com/lyssiev/dvwa-idor.git'
  - 'cd dvwa-idor'
- Build containers using:
  - 'docker compose up --build'

### This will:
- Build the two containers
- Run Django on http://localhost:8000
- Run the Flask API internally
### To access the application, open your browser and go to http://localhost:8000.
## Common issues
- Port conflicts: Make sure no other services are running on 8000 or 5000
- Reset environment using: 'docker compose down -v', 'docker compose up --build'

