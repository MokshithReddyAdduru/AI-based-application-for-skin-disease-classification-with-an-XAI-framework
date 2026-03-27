Skin Diagnosis AI System: Quick Start Guide

This guide provides the necessary commands to launch the AI Backend Service (Python/Flask) and the Mobile App Frontend (React Native).



Prerequisite: Ensure Python 3.9+, Node.js/npm, and ngrok are installed on your machine. Expo go app in mobile phone



1\. Setup and Installation

A. Install Python Dependencies

Navigate into the backend service folder:



**Bash**



**cd Backend**



Create and activate the Python environment:



**Bash**



**python -m venv venv**

**source venv/Scripts/activate**



Install all Python libraries (TensorFlow, Flask, etc.):



**Bash**



**pip install -r requirements.txt**





B. Install Node/React Dependencies



Navigate into the mobile app folder (after exiting the venv):



Bash



cd ../Frontend

Install all JavaScript libraries:



Bash



npm install



2\. Launch the AI Backend (Terminal 1)

This terminal runs the server that hosts the CNN model.



Return to the backend folder and activate the environment:



Bash



cd ../Backend

source venv/Scripts/activate



Start the API Server:



**Bash**



**python api\_server.py**

**(KEEP THIS TERMINAL OPEN. It should show "Running on http://0.0.0.0:5000".)**



3\. Configure and Launch Frontend (Terminal 2 \& 3)



A. Start ngrok Tunnel (Terminal 2)

Open a NEW Terminal (or CMD/Git Bash).



Navigate to the location of your ngrok.exe file.



Start the Tunnel:



**Bash**



**ngrok http 5000**

**COPY the new HTTPS Forwarding URL (e.g., https://\[random-string].ngrok-free.app).**



B. Update and Run the App (Terminal 3)

Open a THIRD Terminal and navigate to Frontend/.



**Update App.js: Paste the NEW ngrok URL into the API\_URL variable inside App.js.**



Launch the App Server:



**Bash**



**npm start**



**Test: Scan the QR code with your phone's Expo Go app to load the diagnosis screen and test the full pipeline.**

