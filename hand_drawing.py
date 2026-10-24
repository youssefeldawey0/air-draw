"""Hand-tracking drawing engine built on MediaPipe Hands.

Gestures (hand upright, palm facing the camera):
    index finger only ............ draw
    index + middle ............... hover (move without drawing)
    index + middle + ring ........ eraser
    open palm (4 fingers), hold .. clear the canvas
"""
import time

import cv2
import mediapipe as mp
import numpy as np


class HandDrawer:
    # Landmark ids for fingertips (index, middle, ring, pinky) and their PIP joints
    TIPS = (8, 12, 16, 20)
    PIPS = (6, 10, 14, 18)

    def __init__(
        self,
        color=(0, 0, 255),  # BGR
        thickness=6,
        detection_confidence=0.7,
        tracking_confidence=0.6,
        smoothing=0.5,
        clear_hold_seconds=1.2,
    ):
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        self.color = color
        self.thickness = thickness
        self.smoothing = smoothing  # 0 = raw, closer to 1 = smoother but laggier
        self.clear_hold_seconds = clear_hold_seconds
        self.show_landmarks = True

        self.canvas = None
        self.mode = "No hand"
        self._prev_point = None
        self._smooth_point = None
        self._clear_started = None

    # ------------------------------------------------------------------ helpers
    @classmethod
    def fingers_up(cls, landmarks):
        """Return [index, middle, ring, pinky] booleans (True = finger extended)."""
        return [landmarks[t].y < landmarks[p].y for t, p in zip(cls.TIPS, cls.PIPS)]

    def _smooth(self, point):
        if self._smooth_point is None:
            self._smooth_point = np.array(point, dtype=float)
        else:
            s = self.smoothing
            self._smooth_point = s * self._smooth_point + (1 - s) * np.array(point, dtype=float)
        return int(self._smooth_point[0]), int(self._smooth_point[1])

    def clear(self):
        if self.canvas is not None:
            self.canvas[:] = 0
        self._prev_point = None

    def export_png(self):
        """Return the drawing as PNG bytes on a white background (None if empty)."""
        if self.canvas is None:
            return None
        img = np.full_like(self.canvas, 255)
        mask = self.canvas.any(axis=2)
        img[mask] = self.canvas[mask]
        ok, buf = cv2.imencode(".png", img)
        return buf.tobytes() if ok else None

    def close(self):
        self._hands.close()

    # --------------------------------------------------------------------- main
    def process(self, frame_bgr):
        """Take a BGR webcam frame, return the annotated BGR frame with drawing."""
        frame = cv2.flip(frame_bgr, 1)  # mirror so movement feels natural
        h, w = frame.shape[:2]
        if self.canvas is None or self.canvas.shape[:2] != (h, w):
            self.canvas = np.zeros((h, w, 3), dtype=np.uint8)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)

        cursor = None
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            if self.show_landmarks:
                self._mp_draw.draw_landmarks(frame, hand, self._mp_hands.HAND_CONNECTIONS)

            lm = hand.landmark
            index, middle, ring, pinky = self.fingers_up(lm)
            tip = (int(lm[8].x * w), int(lm[8].y * h))
            cursor = self._smooth(tip)

            if index and middle and ring and pinky:
                self.mode = "Clear (hold palm)"
                self._prev_point = None
                now = time.time()
                if self._clear_started is None:
                    self._clear_started = now
                elif now - self._clear_started >= self.clear_hold_seconds:
                    self.clear()
                    self._clear_started = now
            else:
                self._clear_started = None
                if index and not middle and not ring and not pinky:
                    self.mode = "Drawing"
                    if self._prev_point is not None:
                        cv2.line(self.canvas, self._prev_point, cursor,
                                 self.color, self.thickness, cv2.LINE_AA)
                    self._prev_point = cursor
                elif index and middle and ring and not pinky:
                    self.mode = "Eraser"
                    radius = self.thickness * 3
                    if self._prev_point is not None:
                        cv2.line(self.canvas, self._prev_point, cursor, (0, 0, 0), radius * 2)
                    cv2.circle(self.canvas, cursor, radius, (0, 0, 0), -1)
                    self._prev_point = cursor
                elif index and middle and not ring and not pinky:
                    self.mode = "Hover"
                    self._prev_point = None
                else:
                    self.mode = "Idle"
                    self._prev_point = None
        else:
            self.mode = "No hand"
            self._prev_point = None
            self._smooth_point = None
            self._clear_started = None

        # Overlay the drawing on the camera frame
        mask = self.canvas.any(axis=2)
        frame[mask] = self.canvas[mask]

        # Cursor + status text
        if cursor is not None:
            if self.mode == "Eraser":
                cv2.circle(frame, cursor, self.thickness * 3, (255, 255, 255), 2)
            elif self.mode == "Drawing":
                cv2.circle(frame, cursor, self.thickness // 2 + 3, self.color, -1)
            else:
                cv2.circle(frame, cursor, 10, (255, 255, 255), 2)
        cv2.putText(frame, self.mode, (12, 32), cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(frame, self.mode, (12, 32), cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (255, 255, 255), 2, cv2.LINE_AA)
        return frame
