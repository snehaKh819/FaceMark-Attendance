# File: facemark_core.py

import os
import cv2
import pickle
import numpy as np
from datetime import datetime
from keras_facenet import FaceNet
from sklearn.metrics.pairwise import cosine_similarity

EMBEDDINGS_FILE = "embeddings.pkl"
IMAGES_DIR = "student_images"
ATTENDANCE_DIR = "attendance_logs"

embedder = FaceNet()

# Ensure necessary directories exist
def ensure_dirs():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)

def load_embeddings():
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_embeddings(embeddings):
    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(embeddings, f)

def register_student(name):
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    os.makedirs(f"{IMAGES_DIR}/{name}", exist_ok=True)
    count = 0
    max_images = 10
    embeddings = []

    print("Press 'c' to capture face images.")

    while count < max_images:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            face = cv2.resize(face, (160, 160))
            cv2.imshow("Registering...", face)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('c'):
                cv2.imwrite(f"{IMAGES_DIR}/{name}/{count}.jpg", face)
                emb = embedder.embeddings([face])[0]
                embeddings.append(emb)
                count += 1
                break

        cv2.imshow("Live", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if embeddings:
        data = load_embeddings()
        data[name] = np.mean(embeddings, axis=0)
        save_embeddings(data)
        print(f"[✔] {name} has been registered successfully.")
    else:
        print("[!] No face data captured.")

def mark_attendance_from_video(video_path):
    if not os.path.exists(video_path):
        print(f"[!] Video not found: {video_path}")
        return

    embeddings = load_embeddings()
    if not embeddings:
        print("[!] No registered embeddings found.")
        return

    cap = cv2.VideoCapture(video_path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    marked = set()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = frame[y:y + h, x:x + w]
            face = cv2.resize(face, (160, 160))
            embedding = embedder.embeddings([face])[0]

            best_match = None
            best_score = 0.0

            for name, ref_embed in embeddings.items():
                score = cosine_similarity([embedding], [ref_embed])[0][0]
                if score > best_score:
                    best_score = score
                    best_match = name

            if best_score > 0.5:
                if best_match not in marked:
                    marked.add(best_match)
                cv2.putText(frame, best_match, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Video Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{ATTENDANCE_DIR}/attendance_{timestamp}.csv"
    with open(filename, "w") as f:
        f.write("Name,Timestamp\n")
        for name in marked:
            f.write(f"{name},{datetime.now().strftime('%H:%M:%S')}\n")

    print(f"[✔] Attendance saved for {len(marked)} students to {filename}")

# Run `open_home()` from GUI file to start app
