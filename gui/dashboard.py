# dashboard.py - Main dashboard/home screen functionality

import customtkinter as ctk
from tkinter import messagebox
from .styles import *
from .components import ModernButton

def show_error(title, message):
    """Show error message with traceback in development"""
    import traceback
    error_msg = f"{message}\n\nTraceback:\n{traceback.format_exc()}"
    messagebox.showerror(title, error_msg)

def show_home(session, open_registration_callback, open_attendance_callback, open_history_callback, open_students_callback):
    """Display the home screen"""
    try:
        home_win = ctk.CTk()
        home_win.title("FaceMark - Home")
        home_win.state("zoomed")
        home_win.resizable(False, False)
        home_win.minsize(1000, 800)

        # Main container
        main_container = ctk.CTkFrame(home_win, fg_color=VIBRANT_BG)
        main_container.pack(fill="both", expand=True)

        # Header with faculty info
        header_frame = ctk.CTkFrame(main_container, fg_color=VIBRANT_LIGHT, height=120)
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)

        # Faculty info
        faculty_info = ctk.CTkFrame(header_frame, fg_color="transparent")
        faculty_info.pack(side="left", padx=30, pady=20)

        ctk.CTkLabel(
            faculty_info,
            text=f"👨‍🏫 {session.get('faculty_name', 'Faculty')}",
            font=FONT_HEADER,
            text_color=VIBRANT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            faculty_info,
            text=f"📚 Subject: Computer Science",
            font=FONT_BODY,
            text_color=VIBRANT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))

        # Welcome message
        welcome_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        welcome_frame.pack(side="right", padx=30, pady=20)

        ctk.CTkLabel(
            welcome_frame,
            text="Welcome to FaceMark",
            font=FONT_SUBHEADER,
            text_color=VIBRANT_ACCENT
        ).pack(anchor="e")

        ctk.CTkLabel(
            welcome_frame,
            text="Facial Recognition Attendance System",
            font=FONT_SMALL,
            text_color=VIBRANT_SECONDARY
        ).pack(anchor="e", pady=(5, 0))

        # Main content area
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Grid for buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(expand=True)

        # Configure grid weights
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)

        # Registration button
        reg_btn = ModernButton(
            button_frame,
            text="📝 Student Registration",
            command=open_registration_callback,
            height=120,
            font=FONT_HEADER
        )
        reg_btn.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Mark Attendance button
        attendance_btn = ModernButton(
            button_frame,
            text="📊 Mark Attendance",
            command=open_attendance_callback,
            height=120,
            font=FONT_HEADER
        )
        attendance_btn.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Attendance History button
        history_btn = ModernButton(
            button_frame,
            text="📈 Attendance History",
            command=open_history_callback,
            height=120,
            font=FONT_HEADER
        )
        history_btn.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Registered Students button
        students_btn = ModernButton(
            button_frame,
            text="👥 Registered Students",
            command=open_students_callback,
            height=120,
            font=FONT_HEADER
        )
        students_btn.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        home_win.mainloop()
    except Exception as e:
        show_error("Application Error", str(e)) 