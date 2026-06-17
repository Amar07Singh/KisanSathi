import os
import cv2
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import time
import threading
from collections import deque
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av

# =========================
# MUST BE AT VERY TOP
# =========================
if "shared" not in st.session_state:
    st.session_state.shared = {
        "latest_prob": 0.0,
        "latest_label": "IDLE",
        "smoothed_prob": 0.0,
        "face_detected": False,
        "fps": 0.0,
        "lock": threading.Lock(),
    }

if "prob_history" not in st.session_state:
    st.session_state.prob_history = deque(maxlen=120)
if "time_history" not in st.session_state:
    st.session_state.time_history = deque(maxlen=120)
if "pain_events" not in st.session_state:
    st.session_state.pain_events = []
if "frame_count" not in st.session_state:
    st.session_state.frame_count = 0
if "pain_count" not in st.session_state:
    st.session_state.pain_count = 0

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Pain Detection", layout="wide")

# =========================
# MODEL LOAD
# =========================
@st.cache_resource
def load_model(path):
    import tensorflow as tf
    return tf.keras.models.load_model(path, compile=False)

# =========================
# PREPROCESS
# =========================
IMG_SIZE = (128, 128)

def preprocess(face):
    face = cv2.resize(face, IMG_SIZE)
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    face = face.astype("float32") / 255.0
    return np.expand_dims(face, axis=0)

# =========================
# VIDEO PROCESSOR
# =========================
class PainVideoProcessor(VideoProcessorBase):
    def __init__(self, model, shared):
        self.model = model
        self.shared = shared
        self.buffer = deque(maxlen=5)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.threshold = 0.4
        self.prev_time = time.time()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        fps = 1 / (time.time() - self.prev_time)
        self.prev_time = time.time()

        shared = self.shared

        if len(faces) > 0:
            x, y, w, h = faces[0]
            face = img[y:y+h, x:x+w]

            arr = preprocess(face)
            prob = float(self.model.predict(arr, verbose=0)[0][0])

            self.buffer.append(prob)
            smoothed = np.mean(self.buffer)

            label = "PAIN" if smoothed > self.threshold else "NO PAIN"

            with shared["lock"]:
                shared["latest_prob"] = prob
                shared["smoothed_prob"] = smoothed
                shared["latest_label"] = label
                shared["face_detected"] = True
                shared["fps"] = fps

            color = (0, 0, 255) if label == "PAIN" else (0, 255, 0)
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
            cv2.putText(img, f"{label} {smoothed:.2f}",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        else:
            with shared["lock"]:
                shared["latest_label"] = "IDLE"
                shared["face_detected"] = False
                shared["smoothed_prob"] = 0.0
                shared["latest_prob"] = 0.0
                shared["fps"] = fps

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("Settings")

model_path = st.sidebar.text_input("Model path", "MBnet.keras")

if st.sidebar.button("Load Model"):
    try:
        model = load_model(model_path)
        st.session_state.model = model
        st.success("Model Loaded")
    except Exception as e:
        st.error(str(e))

# =========================
# MAIN
# =========================
st.title("Pain Detection Dashboard")

if "model" not in st.session_state:
    st.warning("Load model first")
    st.stop()

shared = st.session_state.shared
model = st.session_state.model

ctx = webrtc_streamer(
    key="test",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=lambda: PainVideoProcessor(model, shared),
    media_stream_constraints={"video": True, "audio": False},
)

# =========================
# UI DISPLAY
# =========================
with shared["lock"]:
    prob = shared["smoothed_prob"]
    label = shared["latest_label"]
    fps = shared["fps"]

st.metric("Status", label)
st.metric("Pain Probability", f"{prob*100:.2f}%")
st.metric("FPS", f"{fps:.1f}")

# =========================
# LOGGING
# =========================
if label == "PAIN":
    st.session_state.pain_events.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "prob": prob
    })
    st.session_state.pain_count += 1

st.subheader("Pain Events")
for e in st.session_state.pain_events[-10:]:
    st.write(f"{e['time']} → {e['prob']:.2f}")




from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000, key="refresh")