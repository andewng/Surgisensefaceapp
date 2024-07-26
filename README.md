# faceidapp
Github repository for DSCP face recognition app on streamlit
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
- face_recognition module
<hr>

## Description
<hr>
- dataset: contains images of people to be recognised, file format: jpg
- pages: contains the code for each page of the app. If you want to add more pages, you can create a new file which format is Order_Icon_Pagename in this folder, or just no-icon page with format Order_Pagename
- Tracking.py: Home page of the app, using for tracking real-time using webcam and picture.
- utils.py: contains the functions utilized by the app.
- config.yaml: contains the configuration for the app such as path of dataset dir and prompt messages.
- requirements.txt: contains the dependencies for the app.
