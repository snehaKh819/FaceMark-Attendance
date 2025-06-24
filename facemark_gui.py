# facemark_gui.py
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from datetime import datetime
import os
import pandas as pd
from facemark_core import register_student, mark_attendance_from_video, ensure_dirs, get_registered_students, delete_registered_student
import traceback

# Session context to store faculty info
session = {
    'faculty_name': '',
    'faculty_id': '',
    'current_section': None  # Will store the currently selected section
}

# Configure appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Define modern professional color palette
VIBRANT_PRIMARY = "#2D3436"      # Deep Charcoal
VIBRANT_SECONDARY = "#636E72"    # Sophisticated Gray
VIBRANT_ACCENT = "#00B894"       # Mint Green
VIBRANT_DARK = "#2D3436"         # Deep Charcoal
VIBRANT_HOVER = "#0984E3"        # Modern Blue
VIBRANT_BG = "#F5F6FA"           # Light Gray
VIBRANT_LIGHT = "#FFFFFF"        # Pure White
VIBRANT_TEXT = "#2D3436"         # Deep Charcoal
VIBRANT_SUCCESS = "#00B894"      # Mint Green
VIBRANT_WARNING = "#FDCB6E"      # Soft Yellow
VIBRANT_SIDEBAR = "#2D3436"      # Deep Charcoal
VIBRANT_BORDER = "#DFE6E9"       # Light Gray Border
VIBRANT_PLACEHOLDER = "#B2BEC3"  # Muted Gray

# Available sections
SECTIONS = ["A", "B", "C", "D"]

def ensure_attendance_logs_dir():
    """Ensure attendance_logs directory exists"""
    if not os.path.exists("attendance_logs"):
        os.makedirs("attendance_logs")

def show_error(title, message):
    """Show error message with traceback in development"""
    error_msg = f"{message}\n\nTraceback:\n{traceback.format_exc()}"
    messagebox.showerror(title, error_msg)

class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color=VIBRANT_BG, corner_radius=10)
        
        # Center the overlay
        self.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add content
        self.label = ctk.CTkLabel(
            self,
            text="Processing...",
            font=("Arial", 14),
            text_color=VIBRANT_DARK
        )
        self.label.pack(pady=20)
        
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=10)
        self.progress.set(0)
        
        # Hide initially
        self.place_forget()

    def show(self):
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.lift()

    def hide(self):
        self.place_forget()

class ModernButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        # Remove fg_color from kwargs if it exists to avoid duplicate
        if 'fg_color' in kwargs:
            del kwargs['fg_color']
        if 'hover_color' in kwargs:
            del kwargs['hover_color']
        if 'text_color' in kwargs:
            del kwargs['text_color']
        # Only set font if not provided
        if 'font' not in kwargs:
            kwargs['font'] = ("Arial", 12, "bold")
        super().__init__(
            master,
            fg_color=VIBRANT_ACCENT,
            hover_color=VIBRANT_HOVER,
            text_color=VIBRANT_LIGHT,
            border_width=0,
            corner_radius=8,
            **kwargs
        )

class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        # Remove color-related kwargs if they exist
        for key in ['fg_color', 'border_color', 'text_color', 'placeholder_text_color']:
            if key in kwargs:
                del kwargs[key]
                
        super().__init__(
            master,
            fg_color=VIBRANT_LIGHT,
            border_color=VIBRANT_BORDER,
            text_color=VIBRANT_TEXT,
            placeholder_text_color=VIBRANT_PLACEHOLDER,
            corner_radius=8,
            font=("Arial", 12),
            **kwargs
        )

def show_login():
    try:
        login_win = ctk.CTk()
        login_win.title("FaceMark Login")
        login_win.state("zoomed")  # This will maximize the window
        login_win.resizable(False, False)
        login_win.minsize(800, 700)  # Set minimum size to make it wider

        # Create main frame with padding
        main_frame = ctk.CTkFrame(login_win, fg_color=VIBRANT_BG)
        main_frame.pack(fill="both", expand=True, padx=80, pady=60)  # Increased padding for wider appearance

        # Logo/Title with modern styling
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 30))
        
        # Add a decorative line above the title
        ctk.CTkFrame(
            title_frame,
            height=4,
            fg_color=VIBRANT_ACCENT,
            corner_radius=2
        ).pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="FaceMark",
            font=("Arial", 36, "bold"),
            text_color=VIBRANT_PRIMARY
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Faculty Login",
            font=("Arial", 18),
            text_color=VIBRANT_SECONDARY
        ).pack(pady=(0, 30))

        # Input fields with modern styling
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=20, padx=60)  # Added horizontal padding for wider form

        name_var = tk.StringVar()
        id_var = tk.StringVar()
        password_var = tk.StringVar()

        # Name field with icon and label
        name_label = ctk.CTkLabel(
            input_frame,
            text="👤 Faculty Name",
            font=("Arial", 12, "bold"),
            text_color=VIBRANT_PRIMARY,
            anchor="w"
        )
        name_label.pack(fill="x", pady=(0, 5))

        ModernEntry(
            input_frame,
            textvariable=name_var,
            placeholder_text="Enter your full name",
            height=45
        ).pack(fill="x", pady=(0, 15))

        # ID field with icon and label
        id_label = ctk.CTkLabel(
            input_frame,
            text="🆔 Faculty ID",
            font=("Arial", 12, "bold"),
            text_color=VIBRANT_PRIMARY,
            anchor="w"
        )
        id_label.pack(fill="x", pady=(0, 5))

        ModernEntry(
            input_frame,
            textvariable=id_var,
            placeholder_text="Enter your faculty ID",
            height=45
        ).pack(fill="x", pady=(0, 15))

        # Password field with icon and label
        password_label = ctk.CTkLabel(
            input_frame,
            text="🔒 Password",
            font=("Arial", 12, "bold"),
            text_color=VIBRANT_PRIMARY,
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 5))

        ModernEntry(
            input_frame,
            textvariable=password_var,
            placeholder_text="Enter your password",
            show="•",
            height=45
        ).pack(fill="x", pady=(0, 15))

        def login():
            try:
                if not name_var.get() or not id_var.get() or not password_var.get():
                    messagebox.showwarning("Input Error", "Please fill in all fields.")
                    return
                if len(password_var.get()) < 6:
                    messagebox.showwarning("Invalid Password", "Password must be at least 6 characters long.")
                    return
                session['faculty_name'] = name_var.get()
                session['faculty_id'] = id_var.get()
                login_win.destroy()
                open_home()
            except Exception as e:
                show_error("Login Error", str(e))

        # Login button with hover effect
        login_btn = ModernButton(
            input_frame,
            text="Login",
            command=login,
            height=50,
            font=("Arial", 16, "bold")
        )
        login_btn.pack(fill="x", pady=(0, 10))

        # Exit button
        exit_btn = ModernButton(
            input_frame,
            text="Exit",
            command=login_win.destroy,
            height=40,
            font=("Arial", 16, "bold"),
            fg_color=VIBRANT_SECONDARY,
            hover_color=VIBRANT_WARNING
        )
        exit_btn.pack(fill="x", pady=(0, 20))

        # Add a decorative line below the login and exit buttons
        ctk.CTkFrame(
            input_frame,
            height=2,
            fg_color=VIBRANT_BORDER,
            corner_radius=1
        ).pack(fill="x", pady=(0, 20))

        login_win.mainloop()
    except Exception as e:
        show_error("Application Error", str(e))

def open_home():
    ensure_dirs()
    app = ctk.CTk()
    app.title("FaceMark Dashboard")
    app.geometry("1200x700")
    app.minsize(1000, 600)

    # Create main container
    main_container = ctk.CTkFrame(app, fg_color=VIBRANT_BG)
    main_container.pack(fill="both", expand=True)

    # Sidebar
    sidebar = ctk.CTkFrame(main_container, width=250, corner_radius=0, fg_color=VIBRANT_SIDEBAR)
    sidebar.pack(side="left", fill="y", padx=0, pady=0)
    sidebar.pack_propagate(False)

    # User info section
    user_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    user_frame.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(
        user_frame,
        text=f"👤 {session['faculty_name']}",
        font=("Arial", 18, "bold"),
        text_color=VIBRANT_LIGHT
    ).pack(anchor="w")
    
    # Section selection
    section_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    section_frame.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(
        section_frame,
        text="Select Section",
        font=("Arial", 14, "bold"),
        text_color=VIBRANT_LIGHT
    ).pack(anchor="w", pady=(0, 10))

    section_var = tk.StringVar(value="Select a section")
    section_menu = ctk.CTkOptionMenu(
        section_frame,
        values=["Select a section"] + SECTIONS,
        variable=section_var,
        height=40,
        font=("Arial", 12),
        fg_color=(VIBRANT_ACCENT, VIBRANT_PRIMARY),
        button_color=(VIBRANT_HOVER, VIBRANT_SECONDARY),
        button_hover_color=(VIBRANT_HOVER, VIBRANT_SECONDARY),
        command=lambda x: update_section(x)
    )
    section_menu.pack(fill="x", pady=5)

    # Navigation buttons
    nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    nav_frame.pack(fill="x", padx=20, pady=20)

    def create_nav_button(text, command, icon):
        btn = ModernButton(
            nav_frame,
            text=f"{icon} {text}",
            command=command,
            height=45,
            anchor="w"
        )
        btn.pack(fill="x", pady=5)
        return btn

    # Main content area
    main_frame = ctk.CTkFrame(main_container, fg_color=VIBRANT_BG)
    main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Loading overlay
    loading = LoadingOverlay(main_frame)

    def update_section(section):
        if section != "Select a section":
            session['current_section'] = section
            # Clear main frame
            for widget in main_frame.winfo_children():
                widget.destroy()
            # Show welcome message with selected section
            show_welcome_message()

    def show_welcome_message():
        welcome_frame = ctk.CTkFrame(main_frame, fg_color=VIBRANT_LIGHT)
        welcome_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            welcome_frame,
            text=f"Welcome, {session['faculty_name']}!",
            font=("Arial", 24, "bold"),
            text_color=VIBRANT_PRIMARY
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        ctk.CTkLabel(
            welcome_frame,
            text=f"Section: {session['current_section']}",
            font=("Arial", 16),
            text_color=VIBRANT_SECONDARY
        ).pack(anchor="w", padx=20, pady=(0, 20))

    def switch_to_register():
        if not session['current_section']:
            messagebox.showwarning("Section Required", "Please select a section first.")
            return
        for widget in main_frame.winfo_children():
            widget.destroy()
        show_register_page(main_frame)

    def switch_to_attendance():
        if not session['current_section']:
            messagebox.showwarning("Section Required", "Please select a section first.")
            return
        for widget in main_frame.winfo_children():
            widget.destroy()
        show_attendance_upload(main_frame)

    def switch_to_history():
        if not session['current_section']:
            messagebox.showwarning("Section Required", "Please select a section first.")
            return
        for widget in main_frame.winfo_children():
            widget.destroy()
        show_attendance_history(main_frame)

    def switch_to_students():
        if not session['current_section']:
            messagebox.showwarning("Section Required", "Please select a section first.")
            return
        for widget in main_frame.winfo_children():
            widget.destroy()
        show_registered_students_page(main_frame)

    def logout():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            app.destroy()
            show_login()

    # Create navigation buttons
    create_nav_button("Register Student", switch_to_register, "🧍")
    create_nav_button("Mark Attendance", switch_to_attendance, "🎥")
    create_nav_button("Attendance History", switch_to_history, "📊")
    create_nav_button("Registered Students", switch_to_students, "📋")
    
    # Logout button at bottom
    logout_btn = ModernButton(
        sidebar,
        text="🚪 Logout",
        command=logout,
        height=45,
        fg_color=VIBRANT_SECONDARY,
        hover_color=VIBRANT_WARNING
    )
    logout_btn.pack(side="bottom", fill="x", padx=20, pady=20)

    # Show initial welcome message
    show_welcome_message()

    app.mainloop()

def show_register_page(frame):
    # Create main container with padding
    container = ctk.CTkFrame(frame, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=40, pady=40)

    # Title
    ctk.CTkLabel(
        container,
        text="Student Registration",
        font=("Arial", 24, "bold"),
        text_color=VIBRANT_PRIMARY
    ).pack(pady=(0, 20))

    # Input form
    form_frame = ctk.CTkFrame(container, fg_color=VIBRANT_LIGHT)
    form_frame.pack(fill="x", pady=20)

    name_var = tk.StringVar()
    roll_var = tk.StringVar()

    # Student details
    details_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    details_frame.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(
        details_frame,
        text="Student Details",
        font=("Arial", 16, "bold"),
        text_color=VIBRANT_PRIMARY
    ).pack(anchor="w", pady=(0, 20))

    # Name field with label
    name_label = ctk.CTkLabel(
        details_frame,
        text="Student Name",
        font=("Arial", 12, "bold"),
        text_color=VIBRANT_PRIMARY,
        anchor="w"
    )
    name_label.pack(fill="x", pady=(0, 5))

    ModernEntry(
        details_frame,
        textvariable=name_var,
        placeholder_text="Enter student's full name",
        height=40
    ).pack(fill="x", pady=(0, 15))

    # Roll number field with label
    roll_label = ctk.CTkLabel(
        details_frame,
        text="Roll Number",
        font=("Arial", 12, "bold"),
        text_color=VIBRANT_PRIMARY,
        anchor="w"
    )
    roll_label.pack(fill="x", pady=(0, 5))

    ModernEntry(
        details_frame,
        textvariable=roll_var,
        placeholder_text="Enter student's roll number",
        height=40
    ).pack(fill="x", pady=(0, 15))

    # Section info
    section_info = ctk.CTkLabel(
        details_frame,
        text=f"Section: {session['current_section']}",
        font=("Arial", 12, "bold"),
        text_color=VIBRANT_SECONDARY,
        anchor="w"
    )
    section_info.pack(fill="x", pady=(0, 15))

    # --- Registered Students List ---
    students_frame = ctk.CTkFrame(container, fg_color=VIBRANT_LIGHT)
    students_frame.pack(fill="both", expand=False, padx=20, pady=10)
    ctk.CTkLabel(
        students_frame,
        text="Registered Students in this Section:",
        font=("Arial", 14, "bold"),
        text_color=VIBRANT_PRIMARY
    ).pack(anchor="w", padx=10, pady=(10, 5))

    # Scrollable area for students
    students_scroll = ctk.CTkScrollableFrame(students_frame, height=120)
    students_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_students_list():
        for widget in students_scroll.winfo_children():
            widget.destroy()
        students = get_registered_students(session['current_section'])
        if not students:
            ctk.CTkLabel(students_scroll, text="No students registered yet.", font=("Arial", 12), text_color=VIBRANT_SECONDARY).pack(anchor="w", padx=5, pady=2)
        else:
            for name, roll, section in students:
                ctk.CTkLabel(students_scroll, text=f"{name} ({roll})", font=("Arial", 12), text_color=VIBRANT_TEXT).pack(anchor="w", padx=5, pady=2)

    refresh_students_list()

    # Preview frame
    preview_frame = ctk.CTkFrame(form_frame, fg_color=VIBRANT_LIGHT)
    preview_frame.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(
        preview_frame,
        text="Student Photo",
        font=("Arial", 16, "bold"),
        text_color=VIBRANT_PRIMARY
    ).pack(anchor="w", pady=(0, 10))

    # Photo preview area
    photo_preview_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
    photo_preview_frame.pack(fill="x", pady=10)

    preview_label = ctk.CTkLabel(
        photo_preview_frame, 
        text="No image selected",
        font=("Arial", 12),
        text_color=VIBRANT_SECONDARY
    )
    preview_label.pack(pady=20)

    # Photo capture/upload buttons
    button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    button_frame.pack(fill="x", padx=20, pady=20)

    # Create a frame for the buttons
    capture_buttons_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
    capture_buttons_frame.pack(fill="x", pady=5)

    def upload_photo():
        if not name_var.get() or not roll_var.get():
            messagebox.showwarning("Input Error", "Please fill in all student details before uploading photo.")
            return

        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Read and process the image
                img = cv2.imread(file_path)
                if img is None:
                    raise Exception("Could not read the image file")
                
                # Convert to RGB for display
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Resize image for preview while maintaining aspect ratio
                height, width = img_rgb.shape[:2]
                max_size = 200
                if height > max_size or width > max_size:
                    scale = max_size / max(height, width)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img_rgb = cv2.resize(img_rgb, (new_width, new_height))
                
                # Convert to PhotoImage
                img_pil = Image.fromarray(img_rgb)
                img_tk = ImageTk.PhotoImage(img_pil)
                
                # Update preview
                preview_label.configure(image=img_tk, text="")
                # Store reference to prevent garbage collection
                preview_label._image = img_tk
                
                # Save the image
                save_path = os.path.join("student_images", f"{roll_var.get()}_{name_var.get()}.jpg")
                cv2.imwrite(save_path, img)
                
                messagebox.showinfo("Success", "Student photo uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")

    def capture_face():
        if not name_var.get() or not roll_var.get():
            messagebox.showwarning("Input Error", "Please fill in all student details before capturing face.")
            return

        try:
            register_student(name_var.get(), roll_var.get(), session['current_section'])
            messagebox.showinfo("Success", "Student registered successfully!")
            refresh_students_list()  # Refresh the list after registration
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register student: {str(e)}")

    # Create buttons side by side
    capture_btn = ModernButton(
        capture_buttons_frame,
        text="📸 Capture Face",
        command=capture_face,
        height=45
    )
    capture_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

    upload_btn = ModernButton(
        capture_buttons_frame,
        text="📤 Upload Photo",
        command=upload_photo,
        height=45
    )
    upload_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

def show_attendance_upload(frame):
    container = ctk.CTkFrame(frame, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=40, pady=40)

    ctk.CTkLabel(
        container,
        text="Mark Attendance",
        font=("Arial", 24, "bold"),
        text_color=VIBRANT_PRIMARY
    ).pack(pady=(0, 20))

    upload_frame = ctk.CTkFrame(container, fg_color=VIBRANT_LIGHT)
    upload_frame.pack(fill="x", pady=20)

    path_var = tk.StringVar()

    # --- Marked Students List Frame ---
    marked_frame = ctk.CTkFrame(container, fg_color=VIBRANT_LIGHT)
    marked_frame.pack(fill="x", padx=20, pady=(10, 0))
    marked_students_list = []  # Will hold the last marked students

    def show_marked_students(students):
        for widget in marked_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(marked_frame, text="Attendance marked for:", font=("Arial", 16, "bold"), text_color=VIBRANT_PRIMARY).pack(anchor="w", pady=(25, 5), padx=30)
        scroll = ctk.CTkScrollableFrame(marked_frame, height=180)
        scroll.pack(fill="x", expand=True, padx=30, pady=(15, 15))
        # Table headers
        ctk.CTkLabel(scroll, text="Name", font=("Arial", 14, "bold"), width=160, text_color=VIBRANT_SECONDARY, anchor="w").grid(row=0, column=0, padx=(10, 5), pady=2, sticky="w")
        ctk.CTkLabel(scroll, text="Roll No", font=("Arial", 14, "bold"), width=100, text_color=VIBRANT_SECONDARY, anchor="w").grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ctk.CTkLabel(scroll, text="Section", font=("Arial", 14, "bold"), width=80, text_color=VIBRANT_SECONDARY, anchor="w").grid(row=0, column=2, padx=(5, 10), pady=2, sticky="w")
        if not students:
            ctk.CTkLabel(scroll, text="No students recognized.", font=("Arial", 13), text_color=VIBRANT_SECONDARY).grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        else:
            for idx, (name, roll) in enumerate(students, start=1):
                ctk.CTkLabel(scroll, text=name, font=("Arial", 13), width=160, text_color=VIBRANT_TEXT, anchor="w").grid(row=idx, column=0, padx=(10, 5), pady=3, sticky="w")
                ctk.CTkLabel(scroll, text=roll, font=("Arial", 13), width=100, text_color=VIBRANT_TEXT, anchor="w").grid(row=idx, column=1, padx=5, pady=3, sticky="w")
                ctk.CTkLabel(scroll, text=session['current_section'], font=("Arial", 13), width=80, text_color=VIBRANT_TEXT, anchor="w").grid(row=idx, column=2, padx=(5, 10), pady=3, sticky="w")
        # Button to go to Attendance History
        def goto_history():
            for widget in frame.winfo_children():
                widget.destroy()
            show_attendance_history(frame)
        ctk.CTkButton(marked_frame, text="Go to Attendance History", command=goto_history, width=200).pack(pady=(10, 20))

    def browse():
        file = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov")]
        )
        if file:
            path_var.set(file)

    def process():
        if not path_var.get():
            messagebox.showwarning("Error", "No video file selected")
            return

        # Show loading overlay
        loading = LoadingOverlay(frame)
        loading.show()
        frame.update()

        try:
            result = mark_attendance_from_video(path_var.get(), session['current_section'])
            success, marked_students = result
            if success:
                show_marked_students(marked_students)
            else:
                show_marked_students([])
                messagebox.showwarning("No Attendance", "No students were recognized or registered for this section.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            loading.hide()

    # File selection
    file_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
    file_frame.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(
        file_frame,
        text="Select Class Video",
        font=("Arial", 16, "bold"),
        text_color=VIBRANT_PRIMARY
    ).pack(anchor="w", pady=(0, 10))

    path_entry = ModernEntry(
        file_frame,
        textvariable=path_var,
        placeholder_text="Select video file...",
        height=40
    )
    path_entry.pack(side="left", fill="x", expand=True, pady=5)

    ModernButton(
        file_frame,
        text="Browse",
        command=browse,
        width=100,
        height=40
    ).pack(side="right", padx=(10, 0), pady=5)

    # Process button
    ModernButton(
        upload_frame,
        text="🎥 Process Video",
        command=process,
        height=45
    ).pack(fill="x", padx=20, pady=20)

def show_attendance_history(frame):
    try:
        ensure_attendance_logs_dir()
        
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=40)

        # Header with title and download button
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text="Attendance History",
            font=("Arial", 24, "bold"),
            text_color=VIBRANT_PRIMARY
        ).pack(side="left")

        def refresh_history():
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            load_attendance_logs()

        def download_excel():
            try:
                # Get all CSV files
                log_dir = "attendance_logs"
                if os.path.exists(log_dir):
                    csv_files = [f for f in os.listdir(log_dir) if f.endswith(".csv")]
                    
                    if not csv_files:
                        messagebox.showwarning("No Data", "No attendance logs found to export.")
                        return
                    
                    # Create a timestamp for the folder
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    export_dir = f"attendance_logs/exports_{timestamp}"
                    os.makedirs(export_dir, exist_ok=True)
                    
                    # Export each CSV as individual Excel file
                    exported_files = []
                    for log_file in csv_files:
                        log_path = os.path.join(log_dir, log_file)
                        df = pd.read_csv(log_path)
                        excel_name = log_file.replace(".csv", ".xlsx")
                        excel_path = os.path.join(export_dir, excel_name)
                        df.to_excel(excel_path, engine='openpyxl', index=False)
                        exported_files.append(excel_name)
                    
                    messagebox.showinfo("Success", f"Excel files exported successfully!\nLocation: {export_dir}\nFiles: {', '.join(exported_files)}")
                else:
                    messagebox.showwarning("No Data", "No attendance logs directory found.")
            except Exception as e:
                show_error("Download Error", str(e))

        # Download button
        download_btn = ModernButton(
            header_frame,
            text="📥 Download Excel Report",
            command=download_excel,
            height=40
        )
        download_btn.pack(side="right")

        # Refresh button
        refresh_btn = ModernButton(
            header_frame,
            text="🔄 Refresh",
            command=refresh_history,
            height=40
        )
        refresh_btn.pack(side="right", padx=(0, 10))

        # Clear History button
        def clear_history():
            if messagebox.askyesno("Confirm Clear", "Are you sure you want to delete all attendance history? This cannot be undone."):
                log_dir = "attendance_logs"
                removed = False
                if os.path.exists(log_dir):
                    for log_file in os.listdir(log_dir):
                        if log_file.endswith(".csv"):
                            try:
                                os.remove(os.path.join(log_dir, log_file))
                                removed = True
                            except Exception as e:
                                show_error("Delete Error", f"Could not delete {log_file}: {str(e)}")
                if removed:
                    messagebox.showinfo("Success", "Attendance history cleared.")
                else:
                    messagebox.showinfo("Info", "No attendance logs to clear.")
                refresh_history()

        clear_btn = ModernButton(
            header_frame,
            text="🗑️ Clear History",
            command=clear_history,
            height=40,
            fg_color=VIBRANT_WARNING,
            hover_color=VIBRANT_ACCENT
        )
        clear_btn.pack(side="right", padx=(0, 10))

        # Create a scrollable frame for attendance records
        scroll_frame = ctk.CTkScrollableFrame(container)
        scroll_frame.pack(fill="both", expand=True)

        def load_attendance_logs():
            log_dir = "attendance_logs"
            section = session.get('current_section')
            if not section:
                ctk.CTkLabel(scroll_frame, text="Please select a section to view its attendance history.", font=("Arial", 14), text_color=VIBRANT_WARNING).pack(anchor="w", padx=10, pady=10)
                return
            found = False
            if os.path.exists(log_dir):
                for log_file in os.listdir(log_dir):
                    if log_file.endswith(".csv") and f"_{section}_" in log_file:
                        found = True
                        log_path = os.path.join(log_dir, log_file)
                        try:
                            df = pd.read_csv(log_path)
                            # Create a card for each log
                            card = ctk.CTkFrame(scroll_frame, fg_color=VIBRANT_LIGHT)
                            card.pack(fill="x", pady=5, padx=5)
                            # Card header with date and download button
                            card_header = ctk.CTkFrame(card, fg_color="transparent")
                            card_header.pack(fill="x", padx=10, pady=5)
                            ctk.CTkLabel(
                                card_header,
                                text=log_file.replace(".csv", ""),
                                font=("Arial", 14, "bold"),
                                text_color=VIBRANT_PRIMARY
                            ).pack(side="left")
                            def download_single_sheet(file_path=log_path, sheet_name=log_file.replace(".csv", "")):
                                try:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    excel_path = f"attendance_logs/{sheet_name}_{timestamp}.xlsx"
                                    df = pd.read_csv(file_path)
                                    df.to_excel(excel_path, engine='openpyxl', index=False)
                                    messagebox.showinfo("Success", f"Excel sheet downloaded successfully!\nSaved as: {excel_path}")
                                except Exception as e:
                                    show_error("Download Error", str(e))
                            ModernButton(
                                card_header,
                                text="📥 Download Sheet",
                                command=lambda p=log_path, s=log_file.replace(".csv", ""): download_single_sheet(p, s),
                                height=30,
                                width=120
                            ).pack(side="right")
                            # Create a table-like display
                            table_frame = ctk.CTkFrame(card, fg_color="transparent")
                            table_frame.pack(fill="x", padx=10, pady=5)
                            # Headers
                            headers = ["Name", "Roll No", "Section", "Time"]
                            for i, header in enumerate(headers):
                                ctk.CTkLabel(
                                    table_frame,
                                    text=header,
                                    font=("Arial", 12, "bold"),
                                    width=100,
                                    text_color=VIBRANT_SECONDARY
                                ).grid(row=0, column=i, padx=5, pady=2)
                            # Data rows
                            for row_idx, (_, row) in enumerate(df.iterrows()):
                                for col_idx, value in enumerate(row):
                                    ctk.CTkLabel(
                                        table_frame,
                                        text=str(value),
                                        font=("Arial", 12),
                                        width=100,
                                        text_color=VIBRANT_TEXT
                                    ).grid(row=row_idx+1, column=col_idx, padx=5, pady=2)
                        except Exception as e:
                            print(f"Error reading {log_file}: {str(e)}")
            if not found:
                ctk.CTkLabel(scroll_frame, text=f"No attendance history for section {section}.", font=("Arial", 14), text_color=VIBRANT_SECONDARY).pack(anchor="w", padx=10, pady=10)
        # Initial load
        load_attendance_logs()
    except Exception as e:
        show_error("Attendance History Error", str(e))

def show_registered_students_page(frame):
    container = ctk.CTkFrame(frame, fg_color=VIBRANT_LIGHT)
    container.pack(fill="both", expand=True, padx=40, pady=40)

    ctk.CTkLabel(
        container,
        text=f"Registered Students - Section {session['current_section']}",
        font=("Arial", 24, "bold"),
        text_color=VIBRANT_PRIMARY
    ).pack(anchor="w", pady=(20, 20), padx=20)

    students_scroll = ctk.CTkScrollableFrame(container, height=400, fg_color=VIBRANT_LIGHT)
    students_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # Table headers (only Name and Roll No)
    ctk.CTkLabel(students_scroll, text="Name", font=("Arial", 14, "bold"), width=200, text_color=VIBRANT_SECONDARY, anchor="w").grid(row=0, column=0, padx=10, pady=2, sticky="w")
    ctk.CTkLabel(students_scroll, text="Roll No", font=("Arial", 14, "bold"), width=120, text_color=VIBRANT_SECONDARY, anchor="w").grid(row=0, column=1, padx=10, pady=2, sticky="w")
    ctk.CTkLabel(students_scroll, text="", width=60).grid(row=0, column=2)  # For delete button column

    students = get_registered_students(session['current_section'])
    def refresh():
        for widget in students_scroll.winfo_children():
            widget.destroy()
        ctk.CTkLabel(students_scroll, text="Name", font=("Arial", 14, "bold"), width=200, text_color=VIBRANT_SECONDARY, anchor="w").grid(row=0, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(students_scroll, text="Roll No", font=("Arial", 14, "bold"), width=120, text_color=VIBRANT_SECONDARY, anchor="w").grid(row=0, column=1, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(students_scroll, text="", width=60).grid(row=0, column=2)
        students = get_registered_students(session['current_section'])
        if not students:
            ctk.CTkLabel(students_scroll, text="No students registered yet.", font=("Arial", 14), text_color=VIBRANT_SECONDARY).grid(row=1, column=0, columnspan=3, padx=5, pady=10, sticky="w")
        else:
            for idx, (name, roll, section) in enumerate(students, start=1):
                ctk.CTkLabel(students_scroll, text=name, font=("Arial", 13), width=200, text_color=VIBRANT_TEXT, anchor="w").grid(row=idx, column=0, padx=10, pady=4, sticky="w")
                ctk.CTkLabel(students_scroll, text=roll, font=("Arial", 13), width=120, text_color=VIBRANT_TEXT, anchor="w").grid(row=idx, column=1, padx=10, pady=4, sticky="w")
                def make_delete_callback(student_name):
                    return lambda: delete_student(student_name)
                del_btn = ModernButton(students_scroll, text="🗑️", width=40, height=32, fg_color=VIBRANT_WARNING, hover_color=VIBRANT_ACCENT, command=make_delete_callback(name))
                del_btn.grid(row=idx, column=2, padx=5, pady=4)
    def delete_student(student_name):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {student_name}? This cannot be undone."):
            delete_registered_student(student_name)
            refresh()
    refresh()

if __name__ == "__main__":
    try:
        ensure_dirs()
        show_login()
    except Exception as e:
        show_error("Application Error", str(e))
