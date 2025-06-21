# facemark_gui.py
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from datetime import datetime
import os
import pandas as pd
from facemark_core import register_student, mark_attendance_from_video, ensure_dirs
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
            font=("Arial", 14, "bold")
        )
        login_btn.pack(fill="x", pady=(0, 10))

        # Exit button
        exit_btn = ModernButton(
            input_frame,
            text="Exit",
            command=login_win.destroy,
            height=40,
            font=("Arial", 12, "bold"),
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

    def logout():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            app.destroy()
            show_login()

    # Create navigation buttons
    create_nav_button("Register Student", switch_to_register, "🧍")
    create_nav_button("Mark Attendance", switch_to_attendance, "🎥")
    create_nav_button("Attendance History", switch_to_history, "📊")
    
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
            if result:
                messagebox.showinfo("Success", "Attendance marked successfully!")
            else:
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

        # Create a scrollable frame for attendance records
        scroll_frame = ctk.CTkScrollableFrame(container)
        scroll_frame.pack(fill="both", expand=True)

        # Get attendance logs
        log_dir = "attendance_logs"
        if os.path.exists(log_dir):
            for log_file in os.listdir(log_dir):
                if log_file.endswith(".csv"):
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
    except Exception as e:
        show_error("Attendance History Error", str(e))

if __name__ == "__main__":
    try:
        ensure_dirs()
        show_login()
    except Exception as e:
        show_error("Application Error", str(e))
