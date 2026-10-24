# ✍️ Air Draw — Draw in the Air with Hand Tracking

Draw in the air using your index finger and your webcam! 🎨

Air Draw is a computer vision application built with **MediaPipe**, **OpenCV**, and **Streamlit**. It tracks your hand in real time and lets you draw, erase, and interact with a virtual canvas using simple hand gestures.

## ✨ Features

- 🖐️ Real-time hand tracking
- ✍️ Draw using your index finger
- ✌️ Hover without drawing
- 🧹 Erase using hand gestures
- 🎨 Customize brush color and thickness
- 🎯 Adjustable drawing smoothness
- 🦴 Toggle hand skeleton visualization
- 📥 Download your drawing as a PNG image

## 🛠️ Tech Stack

- Python
- MediaPipe
- OpenCV
- Streamlit
- streamlit-webrtc
- NumPy

## 📁 Project Structure

```text
hand-drawing-app/
├── app.py                # Streamlit application
├── hand_drawing.py       # Hand tracking and drawing engine
├── hand_tracking.ipynb   # Jupyter notebook
├── requirements.txt      # Project dependencies
└── README.md
```

## 🚀 Installation

**1. Clone the repository**

```bash
git clone https://github.com/youssefeldawey0/air-draw
cd hand-drawing-app
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

**3. Activate the virtual environment**

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

## ▶️ Run the App

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, allow camera access, and click **START** to begin drawing.

> **Note:** Python 3.9–3.12 is the intended range for this project. Python 3.11 is recommended for compatibility with the specified MediaPipe versions.

## 🖐️ Gesture Controls

| Gesture                           | Action                |
| --------------------------------- | --------------------- |
| ☝️ Index finger only              | Draw                  |
| ✌️ Index + middle fingers         | Hover without drawing |
| 🤟 Index + middle + ring fingers  | Erase                 |
| 🖐️ Open palm held for \~1 second | Clear canvas          |

Use the sidebar to customize your brush, adjust smoothing, toggle the hand skeleton, clear the canvas, and download your drawing.

---

**Built with ❤️ using Python, MediaPipe, OpenCV, and Streamlit.** 🎨
