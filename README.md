# FaceMark: Smart Attendance with Face Recognition 🎯

FaceMark is a smart desktop application designed to automate attendance management using real-time face recognition.  
It processes **recorded classroom videos** to detect, recognize, and log student attendance with minimal human intervention.

---

## 🚀 Features

- Upload a classroom video and automatically mark attendance.
- Face detection using **MTCNN** (Multi-task Cascaded Convolutional Networks).
- Face recognition using **FaceNet** embeddings and **cosine similarity**.
- Simple, user-friendly **Tkinter GUI** to manage operations.
- Attendance reports saved as **CSV files** for easy access.
- Offline application — no internet required once installed.

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **OpenCV** – Video processing and frame handling
- **facenet-pytorch** – Face detection (MTCNN) and recognition (FaceNet)
- **scikit-learn** – Cosine similarity computation
- **Tkinter** – Desktop GUI application
- **NumPy** – Numerical operations
- **Pandas** – Attendance logging into CSV

---

## 📁 Project Structure

```plaintext
FaceMark/
├── main.py                  # Main GUI Application
├── capture_faces.py          # Register new student faces
├── recognize_faces.py        # Attendance marking script
├── embeddings/               # Stored face embeddings (.npy)
├── student_images/           # Captured student face images
├── attendance/               # Attendance CSV reports
├── models/                   # Pretrained FaceNet / MTCNN models
├── utils.py                  # Helper functions
├── requirements.txt          # Python libraries list
└── README.md                 # Project documentation
