# facemark_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import threading
import os
import csv
import customtkinter as ctk
from facemark_core import ensure_dirs, register_student, mark_attendance_from_video, ATTENDANCE_DIR

# Set customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --------- GUI Actions ---------
def gui_register_student():
    # Create a custom dialog for student registration
    dialog = ctk.CTkToplevel()
    dialog.title("Register Student")
    dialog.geometry("400x350")  # Made taller for the test button
    dialog.resizable(False, False)
    
    # Make dialog modal
    dialog.transient(dialog.master)
    dialog.grab_set()
    
    # Variables
    name_var = tk.StringVar()
    roll_var = tk.StringVar()
    section_var = tk.StringVar()
    
    # Form
    ctk.CTkLabel(dialog, text="Student Registration", font=("Arial", 16, "bold")).pack(pady=10)
    
    form_frame = ctk.CTkFrame(dialog)
    form_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Name
    ctk.CTkLabel(form_frame, text="Name:").pack(anchor="w", pady=(10, 0))
    ctk.CTkEntry(form_frame, textvariable=name_var, width=300).pack(pady=(0, 10))
    
    # Roll Number
    ctk.CTkLabel(form_frame, text="Roll Number:").pack(anchor="w", pady=(10, 0))
    ctk.CTkEntry(form_frame, textvariable=roll_var, width=300).pack(pady=(0, 10))
    
    # Section
    ctk.CTkLabel(form_frame, text="Section:").pack(anchor="w", pady=(10, 0))
    ctk.CTkEntry(form_frame, textvariable=section_var, width=300).pack(pady=(0, 10))
    
    # Button frame
    button_frame = ctk.CTkFrame(dialog)
    button_frame.pack(fill="x", padx=20, pady=10)
    
    def test_cam():
        from facemark_core import test_camera
        if test_camera():
            messagebox.showinfo("Camera Test", "Camera is working properly!")
        else:
            messagebox.showerror("Camera Test", "Camera test failed. Please check your camera connection.")
    
    def submit():
        name = name_var.get().strip()
        roll_no = roll_var.get().strip()
        section = section_var.get().strip()
        
        if not name or not roll_no or not section:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        
        dialog.destroy()
        
        # Show instructions to the user
        messagebox.showinfo("Registration", "Press 'c' to capture face images (10 required).\nPress 'q' to quit.")
        
        # Start registration directly instead of in a thread to see any errors
        try:
            print(f"Starting registration for {name}, {roll_no}, {section}")
            register_student(name, roll_no, section)
        except Exception as e:
            print(f"Error during registration: {e}")
            messagebox.showerror("Registration Error", f"An error occurred: {e}")
    
    # Test camera button
    ctk.CTkButton(button_frame, text="Test Camera", command=test_cam).pack(side="left", padx=10)
    
    # Submit button
    ctk.CTkButton(button_frame, text="Register", command=submit).pack(side="right", padx=10)
    
    # Wait for the dialog to be closed
    dialog.wait_window()

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
    home = ctk.CTk()
    home.title("FaceMark Attendance System")
    home.geometry("800x600")
    
    # Main container
    main_frame = ctk.CTkFrame(home)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Header
    header_frame = ctk.CTkFrame(main_frame)
    header_frame.pack(fill="x", pady=20)
    
    ctk.CTkLabel(header_frame, text="FaceMark Attendance System", 
                font=("Helvetica", 24, "bold")).pack(pady=10)
    
    # Buttons container
    buttons_frame = ctk.CTkFrame(main_frame)
    buttons_frame.pack(fill="both", expand=True, pady=20)
    
    # Register button
    register_btn = ctk.CTkButton(
        buttons_frame, 
        text="➕ Register New Student",
        font=("Arial", 14),
        command=gui_register_student,
        width=300,
        height=50
    )
    register_btn.pack(pady=15)
    
    # Attendance button
    attendance_btn = ctk.CTkButton(
        buttons_frame,
        text="📤 Upload Class Video for Attendance",
        font=("Arial", 14),
        command=gui_mark_attendance,
        width=300,
        height=50
    )
    attendance_btn.pack(pady=15)
    
    # Dashboard button
    dashboard_btn = ctk.CTkButton(
        buttons_frame,
        text="📊 View Attendance Dashboard",
        font=("Arial", 14),
        command=open_dashboard,
        width=300,
        height=50
    )
    dashboard_btn.pack(pady=15)
    
    # Footer
    footer_frame = ctk.CTkFrame(main_frame)
    footer_frame.pack(fill="x", pady=10)
    
    ctk.CTkLabel(footer_frame, text="© 2025 FaceMark Attendance System").pack()
    
    home.mainloop()

# --------- Dashboard ---------
def open_dashboard():
    dashboard = ctk.CTkToplevel()
    dashboard.title("Attendance Dashboard")
    dashboard.geometry("800x600")
    
    # Header
    header_frame = ctk.CTkFrame(dashboard)
    header_frame.pack(fill="x", padx=20, pady=20)
    
    ctk.CTkLabel(header_frame, text="Attendance Records", font=("Helvetica", 20, "bold")).pack(pady=10)
    
    # Create tabs
    tab_view = ctk.CTkTabview(dashboard)
    tab_view.pack(fill="both", expand=True, padx=20, pady=20)
    
    records_tab = tab_view.add("Records")
    stats_tab = tab_view.add("Statistics")
    
    # Records tab content
    records_frame = ctk.CTkFrame(records_tab)
    records_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create treeview for attendance records
    columns = ("name", "roll", "section", "date", "time")
    tree = ttk.Treeview(records_frame, columns=columns, show="headings")
    
    # Define headings
    tree.heading("name", text="Student Name")
    tree.heading("roll", text="Roll No")
    tree.heading("section", text="Section")
    tree.heading("date", text="Date")
    tree.heading("time", text="Time")
    
    # Column widths
    tree.column("name", width=150)
    tree.column("roll", width=80)
    tree.column("section", width=80)
    tree.column("date", width=100)
    tree.column("time", width=100)
    
    # Add scrollbar
    scrollbar = ctk.CTkScrollbar(records_frame, command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)
    
    # Load attendance data
    load_attendance_data(tree)
    
    # Stats tab content
    stats_frame = ctk.CTkFrame(stats_tab)
    stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    ctk.CTkLabel(stats_frame, text="Attendance Statistics", font=("Helvetica", 16, "bold")).pack(pady=10)
    
    # Add refresh button
    refresh_btn = ctk.CTkButton(dashboard, text="Refresh Data", command=lambda: load_attendance_data(tree))
    refresh_btn.pack(pady=10)

def load_attendance_data(tree):
    # Clear existing data
    for item in tree.get_children():
        tree.delete(item)
    
    # Get all attendance files
    if not os.path.exists(ATTENDANCE_DIR):
        return
        
    attendance_files = [f for f in os.listdir(ATTENDANCE_DIR) if f.endswith('.csv')]
    
    for file in attendance_files:
        file_path = os.path.join(ATTENDANCE_DIR, file)
        date = file.split('_')[1]  # Extract date from filename
        
        try:
            with open(file_path, 'r') as f:
                csv_reader = csv.reader(f)
                header = next(csv_reader)  # Get header
                
                # Check if this is a new format CSV with roll and section
                has_roll_section = len(header) >= 4
                
                for row in csv_reader:
                    if has_roll_section and len(row) >= 4:
                        name, roll_no, section, time = row[0], row[1], row[2], row[3]
                        tree.insert("", "end", values=(name, roll_no, section, date, time))
                    elif len(row) >= 2:
                        # Handle old format
                        name, time = row[0], row[1]
                        tree.insert("", "end", values=(name, "N/A", "N/A", date, time))
        except Exception as e:
            print(f"Error loading {file}: {e}")

if __name__ == "__main__":
    open_home()
