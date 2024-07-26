import streamlit as st
import cv2
import face_recognition as frg
import yaml
import time
from utils import recognize, build_dataset

st.set_page_config(layout="wide")

# Config
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']

st.sidebar.title("Settings")

# Create a menu bar
menu = ["Image", "Webcam"]
choice = st.sidebar.selectbox("Input type", menu)
# Slider to adjust tolerance
TOLERANCE = st.sidebar.slider("Tolerance", 0.0, 1.0, 0.5, 0.01)
st.sidebar.info("Tolerance is the threshold for face recognition. The lower the tolerance, the more strict the face recognition. The higher the tolerance, the more loose the face recognition.")

# Information section
st.sidebar.title("Healthcare Personnel Information")
name_container = st.sidebar.empty()
id_container = st.sidebar.empty()
verification_status = st.sidebar.empty()
name_container.info('Name: Unknown')
id_container.success('ID: Unknown')

# Initialize variables for tracking verification
verified = False
start_time = None

if choice == "Image":
    st.title("Face Recognition App")
    st.write(PICTURE_PROMPT)
    uploaded_images = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    if uploaded_images:
        for image in uploaded_images:
            image = frg.load_image_file(image)
            image, name, id = recognize(image, TOLERANCE)
            name_container.info(f"Name: {name}")
            id_container.success(f"ID: {id}")
            st.image(image)
            if name != "Unknown":
                verification_status.success("Verified")
            else:
                verification_status.error("Unverified")
    #else:
        #st.info("Please upload an image")

elif choice == "Webcam":
    st.title("Face Recognition App")
    st.write(WEBCAM_PROMPT)
    # Camera Settings
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    FRAME_WINDOW = st.image([])

    while True:
        ret, frame = cam.read()
        if not ret:
            st.error("Failed to capture frame from camera")
            st.info("Please turn off the other app that is using the camera and restart app")
            break
        image, name, id = recognize(frame, TOLERANCE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(image)
        
        # Display name and ID of the person
        name_container.info(f"Name: {name}")
        id_container.success(f"ID: {id}")
        
        # Verification logic
        if name != "Unknown":
            if start_time is None:
                start_time = time.time()
            elif time.time() - start_time >= 3:
                verification_status.success("Verified")
            else:
                verification_status.warning(f"Recognized. Hold still... {int(time.time() - start_time)}s")
        else:
            start_time = None
            verification_status.error("Unverified")


with st.sidebar.form(key='my_form'):
    st.title("Developer Section")
    submit_button = st.form_submit_button(label='REBUILD DATASET')
    if submit_button:
        with st.spinner("Rebuilding dataset..."):
            build_dataset()
        st.success("Dataset has been reset")