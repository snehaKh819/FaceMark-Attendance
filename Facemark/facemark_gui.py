# facemark_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import threading
from facemark_core import ensure_dirs, register_student, mark_attendance_from_video

# --------- GUI Actions ---------
def gui_register_student():
    name = simpledialog.askstring("Register Student", "Enter Student Name:")
    if not name:
        messagebox.showwarning("Input Error", "Student name cannot be empty.")
        return
    register_student(name)
    messagebox.showinfo("Success", f"{name} has been registered successfully.")

def gui_mark_attendance():
    win = tk.Toplevel()
    win.title("Upload Video")
    win.geometry("500x250")
    win.configure(bg="#2e2e2e")

    tk.Label(win, text="Select Class Video", font=("Arial", 14, "bold"),
             bg="#2e2e2e", fg="white").pack(pady=20)

    video_path_var = tk.StringVar()

    def browse_video():
        path = filedialog.askopenfilename(
            title="Select a classroom video",
            filetypes=[("MP4 files", ".mp4"), ("All files", ".*")]
        )
        if path:
            video_path_var.set(path)

    def start_attendance():
        path = video_path_var.get()
        if not path:
            messagebox.showwarning("Warning", "Please select a video file.")
            return
        threading.Thread(target=mark_attendance_from_video, args=(path,)).start()
        messagebox.showinfo("Started", "Attendance process started. It will save a CSV after completion.")

    tk.Entry(win, textvariable=video_path_var, width=50).pack()
    tk.Button(win, text="Browse", command=browse_video, bg="#444", fg="white").pack(pady=10)
    tk.Button(win, text="Start Attendance", command=start_attendance,
              bg="green", fg="white").pack(pady=10)

# --------- Home Page ---------
def open_home():
    ensure_dirs()
    home = tk.Tk()
    home.title("FaceMark Attendance System")
    home.geometry("700x450")
    home.configure(bg="#1e1e1e")

    tk.Label(home, text="FaceMark Attendance System", font=("Helvetica", 20, "bold"),
             bg="#1e1e1e", fg="white").pack(pady=20)

    tk.Button(home, text="➕ Register New Student", font=("Arial", 14),
              bg="#333", fg="white", command=gui_register_student, width=25).pack(pady=15)

    tk.Button(home, text="📤 Upload Class Video for Attendance", font=("Arial", 14),
              bg="#333", fg="white", command=gui_mark_attendance, width=30).pack(pady=10)

    home.mainloop()

if __name__ == "__main__":
    open_home()
