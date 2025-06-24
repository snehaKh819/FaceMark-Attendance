# facemark_core.py

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
HAAR_CASCADE_FILEPATH = os.path.join(os.path.dirname(cv2.__file__), 'data', 'haarcascade_frontalface_default.xml')

embedder = FaceNet()

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

def register_student(name, roll_no, section):
    print(f"[i] Registering {name}, Roll: {roll_no}, Section: {section}")
    student_dir = os.path.join(IMAGES_DIR, name)
    os.makedirs(student_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[!] Camera error")
        return

    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_FILEPATH)
    count = 0
    embeddings = []

    while count < 10:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = frame[y:y + h, x:x + w]
            face = cv2.resize(face, (160, 160))
            emb = embedder.embeddings([face])[0]
            embeddings.append(emb)
            count += 1
            cv2.imwrite(f"{student_dir}/{count}.jpg", face)
            break

        cv2.imshow("Capture", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if embeddings:
        data = load_embeddings()
        data[name] = {
            'embedding': np.mean(embeddings, axis=0),
            'roll_no': roll_no,
            'section': section
        }
        save_embeddings(data)
        print("[✓] Student registered")
    else:
        print("[!] No embeddings captured")

def mark_attendance_from_video(video_path, section=None):
    if not os.path.exists(video_path):
        print("[!] Video not found")
        return False, None

    data = load_embeddings()
    # Filter by section if provided
    if section is not None:
        data = {name: info for name, info in data.items() if info.get('section') == section}
    cap = cv2.VideoCapture(video_path)
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_FILEPATH)
    marked = set()
    student_info = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = frame[y:y + h, x:x + w]
            face = cv2.resize(face, (160, 160))
            emb = embedder.embeddings([face])[0]

            best_match, best_score = None, 0.0
            for name, info in data.items():
                score = cosine_similarity([emb], [info['embedding']])[0][0]
                if score > best_score:
                    best_score = score
                    best_match = name
                    student_info[name] = info

            # Only mark if above threshold and not already marked
            if best_score > 0.5 and best_match not in marked:
                marked.add(best_match)
            # If below threshold, treat as unknown (do not mark)
            # Optionally, you could log or count unknowns here

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if marked:
        section_str = section if section else 'ALL'
        filename = f"{ATTENDANCE_DIR}/attendance_{section_str}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
        with open(filename, 'w') as f:
            f.write("Name,Roll No,Section,Timestamp\n")
            for name in marked:
                info = student_info[name]
                f.write(f"{name},{info['roll_no']},{info['section']},{datetime.now().strftime('%H:%M:%S')}\n")
        print(f"[✓] Attendance saved to {filename}")
        # Prepare marked students list for GUI
        marked_students = [(name, student_info[name]['roll_no']) for name in marked]
        return True, marked_students
    else:
        return False, None
    
def test_accuracy(test_images, true_labels, section=None):
    data = load_embeddings()
    if section is not None:
        data = {name: info for name, info in data.items() if info.get('section') == section}
    correct = 0
    total = len(test_images)
    for img_path, true_name in zip(test_images, true_labels):
        img = cv2.imread(img_path)
        if img is None:
            print(f"Could not read image: {img_path}")
            continue
        face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_FILEPATH)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        found = False
        for (x, y, w, h) in faces:
            face = img[y:y + h, x:x + w]
            face = cv2.resize(face, (160, 160))
            emb = embedder.embeddings([face])[0]
            best_match, best_score = None, 0.0
            for name, info in data.items():
                score = cosine_similarity([emb], [info['embedding']])[0][0]
                if score > best_score:
                    best_score = score
                    best_match = name
            if best_score > 0.5 and best_match == true_name:
                correct += 1
            found = True
            break
        if not found:
            print(f"No face found in {img_path}")
    accuracy = correct / total if total > 0 else 0
    print(f"Accuracy: {accuracy*100:.2f}%")
    return accuracy
        
def get_registered_students(section=None):
    """Return a list of (name, roll_no, section) for all registered students, optionally filtered by section."""
    data = load_embeddings()
    students = []
    for name, info in data.items():
        if section is None or info.get('section') == section:
            students.append((name, info.get('roll_no'), info.get('section')))
    return students
        
def delete_registered_student(name):
    """Delete a registered student by name: remove from embeddings and delete their image directory."""
    data = load_embeddings()
    if name in data:
        del data[name]
        save_embeddings(data)
    # Remove student images directory if exists
    student_dir = os.path.join(IMAGES_DIR, name)
    if os.path.exists(student_dir):
        import shutil
        shutil.rmtree(student_dir)
        
if __name__ == "__main__":
    # Example usage for testing accuracy
    # Replace these with actual image paths and labels as needed
    test_images = ["student_images/Student1/1.jpg", "student_images/Student2/1.jpg"]
    true_labels = ["Student1", "Student2"]
    test_accuracy(test_images, true_labels)
        
