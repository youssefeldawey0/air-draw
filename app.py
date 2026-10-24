import av
import streamlit as st
from streamlit_webrtc import RTCConfiguration, WebRtcMode, webrtc_streamer

from hand_drawing import HandDrawer

st.set_page_config(page_title="Air Draw", page_icon="✍️", layout="wide")

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


def hex_to_bgr(hex_color: str):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (b, g, r)


class DrawingProcessor:
    """Runs on every webcam frame inside streamlit-webrtc's worker thread."""

    def __init__(self):
        self.drawer = HandDrawer()

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        out = self.drawer.process(img)
        return av.VideoFrame.from_ndarray(out, format="bgr24")


# ------------------------------------------------------------------- sidebar
st.sidebar.header("Brush")
color_hex = st.sidebar.color_picker("Colour", "#ff3030")
thickness = st.sidebar.slider("Thickness", 2, 30, 6)
smoothing = st.sidebar.slider("Smoothing", 0.0, 0.9, 0.5, 0.05,
                              help="Higher = smoother lines but more lag")
show_landmarks = st.sidebar.checkbox("Show hand skeleton", value=True)
clear_clicked = st.sidebar.button("🗑️ Clear canvas", use_container_width=True)

# ---------------------------------------------------------------------- main
st.title("✍️ Air Draw")
st.caption("Draw in the air with your index finger — powered by MediaPipe Hands.")

ctx = webrtc_streamer(
    key="air-draw",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=DrawingProcessor,
    media_stream_constraints={
        "video": {"width": {"ideal": 960}, "height": {"ideal": 540}},
        "audio": False,
    },
    async_processing=True,
)

# Push sidebar settings into the running processor
if ctx.video_processor:
    drawer = ctx.video_processor.drawer
    drawer.color = hex_to_bgr(color_hex)
    drawer.thickness = thickness
    drawer.smoothing = smoothing
    drawer.show_landmarks = show_landmarks
    if clear_clicked:
        drawer.clear()

    if st.sidebar.button("📸 Capture drawing", use_container_width=True):
        st.session_state["snapshot"] = drawer.export_png()

if st.session_state.get("snapshot"):
    st.subheader("Captured drawing")
    st.image(st.session_state["snapshot"])
    st.download_button("Download PNG", st.session_state["snapshot"],
                       file_name="air_drawing.png", mime="image/png")

with st.expander("🖐️ Gestures", expanded=True):
    st.markdown(
        """
| Gesture | Action |
|---|---|
| ☝️ Index finger only | **Draw** |
| ✌️ Index + middle | **Hover** (move without drawing) |
| 🤟 Index + middle + ring | **Eraser** |
| 🖐️ Open palm (hold ~1 s) | **Clear** canvas |

Keep your hand upright with the palm facing the camera, in good light.
"""
    )
