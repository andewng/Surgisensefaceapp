import streamlit as st
import cv2
import face_recognition as frg
import yaml
import time
from utils import recognize, build_dataset, submitNew, get_info_from_id, deleteOne
import numpy as np
import pickle
import pandas as pd
from streamlit.components.v1 import html

# Set page configuration
st.set_page_config(layout="wide")

# Load configuration
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.FullLoader)
PICTURE_PROMPT = cfg['INFO']['PICTURE_PROMPT']
WEBCAM_PROMPT = cfg['INFO']['WEBCAM_PROMPT']


# Sidebar settings
st.sidebar.title("Settings")
menu = ["Face Recognition App", "Database", "Updating Database App"]
choice = st.sidebar.selectbox("Select App", menu)

# Passwords for database related apps (Change here)
app_passwords = {
    "Database": "database123",
    "Updating Database App": "update456"
}

# Set Tolerance here
TOLERANCE = 0.4

# Initialize session state
if 'authenticated_app' not in st.session_state:
    st.session_state.authenticated_app = None
if 'verification_status' not in st.session_state:
    st.session_state.verification_status = False
if 'auth_page' not in st.session_state:
    st.session_state.auth_page = False
if 'verified_name' not in st.session_state:
    st.session_state.verified_name = "Unknown"
if 'verified_id' not in st.session_state:
    st.session_state.verified_id = "Unknown"

# Authentication function
def authenticate(app_name, password):
    if app_passwords.get(app_name) == password:
        st.session_state.authenticated_app = app_name
    else:
        st.error("Incorrect password")

# Authentication process
if choice in app_passwords:
    if st.session_state.authenticated_app != choice:
        st.subheader(f"Enter password to access {choice}")
        password = st.text_input("Password", type="password")
        if st.button("Authenticate"):
            authenticate(choice, password)

# Conditional display after authentication is successful
if st.session_state.auth_page:
    st.title("SurgiSense Verification Process Completed.")
    st.write(f"Welcome to SurgiSense, {st.session_state.verified_name}.")
    st.write(f"Healthcare Personnel ID: {st.session_state.verified_id}")
    # Link to SurgiSense Platform
    st.header('Visit our SurgiSense Platform!')
    st.write("Curated for Healthcare Professionals.")
    st.markdown("[Visit our SurgiSense Platform](https://surgisense.streamlit.app/) to access our services.")
    # Link to WIX-powered website front
    st.header('Visit our WIX-powered website front!')
    st.markdown('[Go to SurgiSense WIX-powered website front](https://npdscpproject.wixsite.com/surgisense) to access our services.')
    
    # Link to ChatFuel Bot
    st.markdown('<h5>Chat with our ChatFuel Bot Here!</h5>', unsafe_allow_html=True)
    html('<script id="6635eae9131b2f11614976dd" src="https://dashboard.chatfuel.com/integration/entry-point.js" async defer></script>')

    if st.button("Return"):
        st.session_state.auth_page = False
        st.session_state.verification_status = False
        st.experimental_rerun()  # Refresh the app to go back to main content
else:
    # Display content based on authentication
    if st.session_state.authenticated_app == choice or choice == "Face Recognition App":
        if choice == "Face Recognition App":
            st.title("SurgiSense Face Recognition App")
            input_type = st.sidebar.selectbox("Input type", ["Media", "Face Verification"])

            # Display personnel information
            st.sidebar.title("Healthcare Personnel Information")
            name_container = st.sidebar.empty()
            id_container = st.sidebar.empty()
            verification_status = st.sidebar.empty()
            name_container.info('Name: Unknown')
            id_container.success('ID: Unknown')
            verification_status.error('Unverified')

            if input_type == "Media":
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
                            st.session_state.verification_status = True
                            st.session_state.auth_page = True
                            st.session_state.verified_name = name  # Store verified name
                            st.session_state.verified_id = id      # Store verified ID
                            st.experimental_rerun()  # Force rerun to navigate to the "auth" page
                        else:
                            verification_status.error("Unverified")

            elif input_type == "Face Verification":
                st.write(WEBCAM_PROMPT)
                cam = cv2.VideoCapture(0)
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                FRAME_WINDOW = st.image([])

                start_time = None
                verified = False

                while not st.session_state.verification_status:
                    ret, frame = cam.read()
                    if not ret:
                        st.error("Failed to capture frame from camera")
                        st.info("Please turn off the other app that is using the camera and restart app")
                        break

                    image, name, id = recognize(frame, TOLERANCE)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    FRAME_WINDOW.image(image)

                    name_container.info(f"Name: {name}")
                    id_container.success(f"ID: {id}")

                    if name != "Unknown":
                        if start_time is None:
                            start_time = time.time()
                        elif time.time() - start_time >= 3:
                            verification_status.success("Verified")
                            st.session_state.verification_status = True
                            st.session_state.auth_page = True
                            st.session_state.verified_name = name  # Store verified name
                            st.session_state.verified_id = id      # Store verified ID
                            st.experimental_rerun()  # Force rerun to navigate to the "auth" page
                        else:
                            verification_status.warning(f"Recognized. Hold still... {int(time.time() - start_time)}s")
                    else:
                        start_time = None
                        verification_status.error("Unverified")

        elif choice == "Database":
            st.title("SurgiSense Healthcare Personnel Database")
            cfg = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
            PKL_PATH = cfg['PATH']["PKL_PATH"]

            # Load database
            with open(PKL_PATH, 'rb') as file:
                database = pickle.load(file)

            Index, Id, Name, Image = st.columns([0.5, 0.5, 3, 3])

            for idx, person in database.items():
                with Index:
                    st.write(idx)
                with Id:
                    st.write(person['id'])
                with Name:
                    st.write(person['name'])
                with Image:
                    st.image(person['image'], width=200)

        elif choice == "Updating Database App":
            st.title("Updating SurgiSense Healthcare Personnel Database")
            st.write("This app is used to add new faces to the Healthcare Personnel database or delete existing faces.")

            menu = ["Adding", "Deleting", "Adjusting"]
            choice = st.sidebar.selectbox("Options", menu)
            if choice == "Adding":
                name = st.text_input("Name", placeholder='Enter Name')
                id = st.text_input("ID", placeholder='Enter ID')

                # Create 2 options: Upload image or use webcam
                upload = st.radio("Upload image or use webcam", ("Upload", "Webcam"))
                if upload == "Upload":
                    uploaded_image = st.file_uploader("Upload", type=['jpg', 'png', 'jpeg'])
                    if uploaded_image is not None:
                        st.image(uploaded_image)
                        submit_btn = st.button("Submit", key="submit_btn")
                        if submit_btn:
                            if name == "" or id == "":
                                st.error("Please enter Name and ID")
                            else:
                                ret = submitNew(name, id, uploaded_image)
                                if ret == 1:
                                    st.success("Healthcare Personnel Added")
                                elif ret == 0:
                                    st.error("Healthcare Personnel ID already exists")
                                elif ret == -1:
                                    st.error("The face is not detected in the picture")
                elif upload == "Webcam":
                    img_file_buffer = st.camera_input("Take a picture")
                    submit_btn = st.button("Submit", key="submit_btn")
                    if img_file_buffer is not None:
                        # To read image file buffer with OpenCV:
                        bytes_data = img_file_buffer.getvalue()
                        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                        if submit_btn:
                            if name == "" or id == "":
                                st.error("Please enter name and ID")
                            else:
                                ret = submitNew(name, id, cv2_img)
                                if ret == 1:
                                    st.success("Healthcare Personnel Added")
                                elif ret == 0:
                                    st.error("Healthcare Personnel ID already exists")
                                elif ret == -1:
                                    st.error("The face is not detected in the picture")
            elif choice == "Deleting":
                def del_btn_callback(id):
                    deleteOne(id)
                    st.success("Healthcare Personnel deleted")

                id = st.text_input("ID", placeholder='Enter id')
                submit_btn = st.button("Submit", key="submit_btn")
                if submit_btn:
                    name, image, _ = get_info_from_id(id)
                    if name == None and image == None:
                        st.error("Healthcare Personnel ID does not exist")
                    else:
                        st.success(f"Healthcare Personnel with ID {id} is: {name}")
                        st.warning("Please check the image below to make sure you are deleting the right ID")
                        st.image(image)
                        del_btn = st.button("Delete", key="del_btn", on_click=del_btn_callback, args=(id,))

            elif choice == "Adjusting":
                def form_callback(old_name, old_id, old_image, old_idx):
                    new_name = st.session_state['new_name']
                    new_id = st.session_state['new_id']
                    new_image = st.session_state['new_image']

                    name = old_name
                    id = old_id
                    image = old_image

                    if new_image is not None:
                        image = cv2.imdecode(np.frombuffer(new_image.read(), np.uint8), cv2.IMREAD_COLOR)

                    if new_name != old_name:
                        name = new_name

                    if new_id != old_id:
                        id = new_id

                    ret = submitNew(name, id, image, old_idx=old_idx)
                    if ret == 1:
                        st.success("Healthcare Personnel Added")
                    elif ret == 0:
                        st.error("Healthcare Personnel ID already exists")
                    elif ret == -1:
                        st.error("Face is not detected in the picture")

                id = st.text_input("ID", placeholder='Enter id')
                submit_btn = st.button("Submit", key="submit_btn")
                if submit_btn:
                    old_name, old_image, old_idx = get_info_from_id(id)
                    if old_name == None and old_image == None:
                        st.error("Healthcare Personnel ID does not exist")
                    else:
                        with st.form(key='my_form'):
                            st.title("Adjusting Personnel info")
                            col1, col2 = st.columns(2)
                            new_name = col1.text_input("Name", key='new_name', value=old_name, placeholder='Enter new name')
                            new_id = col1.text_input("ID", key='new_id', value=id, placeholder='Enter new id')
                            new_image = col1.file_uploader("Upload new image", key='new_image', type=['jpg', 'png', 'jpeg'])
                            col2.image(old_image, caption='Current image', width=400)
                            st.form_submit_button(label='Submit', on_click=form_callback, args=(old_name, id, old_image, old_idx))
    else:
        st.warning("Please enter the password to access this section.")
