# login.py - Login screen functionality

import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from .styles import *
from .components import ModernButton, ModernEntry

def show_error(title, message):
    """Show error message with traceback in development"""
    import traceback
    error_msg = f"{message}\n\nTraceback:\n{traceback.format_exc()}"
    messagebox.showerror(title, error_msg)

def show_login(session, open_home_callback):
    """Display the login screen"""
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
            font=FONT_SMALL,
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
            font=FONT_SMALL,
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
            font=FONT_SMALL,
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
                open_home_callback()
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