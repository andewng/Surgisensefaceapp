# FaceApp
Github repository for DSCP SurgiSense face recognition app on streamlit
## Features
<hr>
- Face detection & recognition
- Multi face recognition
- Face verification
<hr>

## Requirements
<hr>
- Python 3.9
- Streamlit 1.22.0
- dlib
- face_recognition module
<hr>

## Description
<hr>
SurgiSense Face recognition & verification app, created for healthcare professionals & personnel, Healthcare professionals can utilise the face verification app locally, Users can log in with the Face Verification App and access main SurgiSense platform to access services such as risk calculator system and WIX platform. 

How the Verification Works:
If user is in the healthcare personnel database, The user will be able to verify themselves through the App, users will have to stay still for 3 seconds to complete the verification process, after this, users will have access to the main SurgiSense streamlit platform

- dataset: contains images of people to be recognised, file format: jpg
- FaceApp.py: Face Recognition & Verification App 
- utils.py: contains the functions utilized by the app.
- config.yaml: contains the configuration for the app such as path of dataset dir and messages in the Face Recognition App
- requirements.txt: contains the dependencies for the app.
- packages.txt: contains the packages for the app used to deploy on Streamlit Cloud.
