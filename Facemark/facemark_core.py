# File: facemark_core.py

import os
import cv2
import pickle
import numpy as np
from datetime import datetime
from keras_facenet import FaceNet
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import messagebox

EMBEDDINGS_FILE = "embeddings.pkl"
IMAGES_DIR = "student_images"
ATTENDANCE_DIR = "attendance_logs"

embedder = FaceNet()

# Ensure necessary directories exist
def ensure_dirs():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    print(f"[i] Directories created/verified: {IMAGES_DIR}, {ATTENDANCE_DIR}")

def load_embeddings():
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_embeddings(embeddings):
    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(embeddings, f)

def register_student(name, roll_no, section):
    print(f"[i] Starting registration for {name}...")
    
    # Create directory for student images
    student_dir = f"{IMAGES_DIR}/{name}"
    os.makedirs(student_dir, exist_ok=True)
    print(f"[i] Created directory: {student_dir}")
    
    # Initialize camera
    print("[i] Opening camera...")
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("[!] Error: Could not open camera.")
        messagebox.showerror("Camera Error", "Could not access the camera. Please check your camera connection.")
        return False
    
    print("[i] Camera opened successfully")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    count = 0
    max_images = 10
    embeddings = []

    print("[i] Press 'c' to capture face images. Press 'q' to quit.")

    # Main capture loop
    while count < max_images:
        ret, frame = cap.read()
        if not ret:
            print("[!] Failed to grab frame from camera")
            break

        # Display counter
        text = f"Captured: {count}/{max_images}"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'c' to capture", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw rectangle around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Display the main frame
        cv2.imshow("Registration", frame)
        
        # Process key presses
        key = cv2.waitKey(1) & 0xFF
        
        # If 'c' is pressed and a face is detected
        if key == ord('c') and len(faces) > 0:
            x, y, w, h = faces[0]  # Use the first detected face
            face = frame[y:y+h, x:x+w]
            
            if face.size > 0:
                face = cv2.resize(face, (160, 160))
                
                # Save image
                img_path = f"{student_dir}/{count}.jpg"
                cv2.imwrite(img_path, face)
                print(f"[i] Saved image {count+1}/{max_images}")
                
                # Generate embedding
                try:
                    emb = embedder.embeddings([face])[0]
                    embeddings.append(emb)
                    count += 1
                except Exception as e:
                    print(f"[!] Error generating embedding: {e}")
                
                # Wait a moment between captures
                cv2.waitKey(500)
        
        # If 'q' is pressed, quit
        elif key == ord('q'):
            print("[i] Registration cancelled.")
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("[i] Camera released and windows closed")

    # Save embeddings if we have any
    if embeddings and count == max_images:
        data = load_embeddings()
        # Store student info along with embedding
        data[name] = {
            'embedding': np.mean(embeddings, axis=0),
            'roll_no': roll_no,
            'section': section
        }
        save_embeddings(data)
        print(f"[✔] {name} has been registered successfully with {count} images.")
        messagebox.showinfo("Success", f"{name} has been registered successfully with {count} images.")
        return True
    else:
        print(f"[!] Registration incomplete. Only {count}/{max_images} images captured.")
        if count > 0:
            messagebox.showwarning("Incomplete", f"Registration incomplete. Only {count}/{max_images} images captured.")
        else:
            messagebox.showerror("Failed", "No face data captured. Registration failed.")
        return False

def mark_attendance_from_video(video_path):
    if not os.path.exists(video_path):
        print(f"[!] Video not found: {video_path}")
        messagebox.showerror("Error", f"Video file not found: {video_path}")
        return

    embeddings = load_embeddings()
    if not embeddings:
        print("[!] No registered embeddings found.")
        messagebox.showerror("Error", "No registered students found. Please register students first.")
        return

    print(f"[i] Opening video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[!] Could not open video: {video_path}")
        messagebox.showerror("Error", f"Could not open video file: {video_path}")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    marked = set()
    student_info = {}  # Store full student info for attendance

    print("[i] Processing video frames...")
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        # Process every 5th frame to speed up
        if frame_count % 5 != 0:
            continue

        # Resize frame for faster processing
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = frame[y:y + h, x:x + w]
            if face.size == 0:
                continue
                
            try:
                face = cv2.resize(face, (160, 160))
                embedding = embedder.embeddings([face])[0]

                best_match = None
                best_score = 0.0

                for name, data in embeddings.items():
                    ref_embed = data['embedding']
                    score = cosine_similarity([embedding], [ref_embed])[0][0]
                    if score > best_score:
                        best_score = score
                        best_match = name
                        student_info[name] = data

                if best_score > 0.5:
                    if best_match not in marked:
                        print(f"[i] Recognized: {best_match} (score: {best_score:.2f})")
                        marked.add(best_match)
                    cv2.putText(frame, f"{best_match} ({best_score:.2f})", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            except Exception as e:
                print(f"[!] Error processing face: {e}")

        # Display frame with recognized faces
        cv2.imshow("Video Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[i] Video processing completed")

    if not marked:
        print("[!] No students recognized in the video")
        messagebox.showwarning("No Matches", "No students were recognized in the video.")
        return

    # Save attendance to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{ATTENDANCE_DIR}/attendance_{timestamp}.csv"
    
    try:
        with open(filename, "w") as f:
            f.write("Name,Roll No,Section,Timestamp\n")
            for name in marked:
                data = student_info.get(name, {})
                roll_no = data.get('roll_no', 'N/A')
                section = data.get('section', 'N/A')
                f.write(f"{name},{roll_no},{section},{datetime.now().strftime('%H:%M:%S')}\n")
        
        print(f"[✔] Attendance saved for {len(marked)} students to {filename}")
        messagebox.showinfo("Success", f"Attendance saved for {len(marked)} students.")
    except Exception as e:
        print(f"[!] Error saving attendance: {e}")
        messagebox.showerror("Error", f"Failed to save attendance: {e}")

def test_camera():
    """Test if the camera can be opened and frames can be read."""
    print("[i] Testing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[!] Error: Could not open camera.")
        return False
    
    # Try to read a few frames
    for i in range(10):
        ret, frame = cap.read()
        if not ret:
            print("[!] Error: Could not read frame from camera.")
            cap.release()
            return False
        
        # Display the frame
        cv2.putText(frame, "Camera Test", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Camera Test", frame)
        cv2.waitKey(100)
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("[i] Camera test successful.")
    return True

# Run `open_home()` from GUI file to start app
