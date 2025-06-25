# attendance.py - Mark attendance functionality

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

def show_attendance(session, facemark_core):
    """Display the mark attendance screen"""
    try:
        attendance_win = ctk.CTk()
        attendance_win.title("FaceMark - Mark Attendance")
        attendance_win.state("zoomed")
        attendance_win.resizable(False, False)
        attendance_win.minsize(1200, 800)

        # Main container
        main_container = ctk.CTkFrame(attendance_win, fg_color=VIBRANT_BG)
        main_container.pack(fill="both", expand=True)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color=VIBRANT_LIGHT, height=100)
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)

        ctk.CTkLabel(
            header_frame,
            text="📊 Mark Attendance",
            font=FONT_TITLE,
            text_color=VIBRANT_PRIMARY
        ).pack(side="left", padx=30, pady=30)

        # Back button
        back_btn = ModernButton(
            header_frame,
            text="← Back to Home",
            command=attendance_win.destroy,
            width=150,
            height=40
        )
        back_btn.pack(side="right", padx=30, pady=30)

        # Content area
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left panel - Attendance controls
        left_panel = ctk.CTkFrame(content_frame, fg_color=VIBRANT_LIGHT)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Controls title
        ctk.CTkLabel(
            left_panel,
            text="Attendance Controls",
            font=FONT_HEADER,
            text_color=VIBRANT_PRIMARY
        ).pack(pady=20)

        # Controls frame
        controls_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        controls_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Section selection
        section_label = ctk.CTkLabel(
            controls_frame,
            text="📚 Select Section",
            font=FONT_SMALL,
            text_color=VIBRANT_PRIMARY,
            anchor="w"
        )
        section_label.pack(fill="x", pady=(0, 5))

        section_var = tk.StringVar(value="A")
        section_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=SECTIONS,
            variable=section_var,
            fg_color=VIBRANT_LIGHT,
            button_color=VIBRANT_ACCENT,
            button_hover_color=VIBRANT_HOVER,
            text_color=VIBRANT_TEXT,
            font=FONT_SMALL,
            height=45
        )
        section_menu.pack(fill="x", pady=(0, 20))

        # Mark attendance button
        mark_btn = ModernButton(
            controls_frame,
            text="📷 Start Attendance",
            command=lambda: mark_attendance(),
            height=60,
            font=FONT_HEADER
        )
        mark_btn.pack(fill="x", pady=(0, 20))

        # Status label
        status_label = ctk.CTkLabel(
            controls_frame,
            text="Ready to mark attendance",
            font=FONT_BODY,
            text_color=VIBRANT_SECONDARY
        )
        status_label.pack(pady=10)

        # Right panel - Marked students list
        right_panel = ctk.CTkFrame(content_frame, fg_color=VIBRANT_LIGHT)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # List title
        list_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        list_header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            list_header,
            text="Marked Students",
            font=FONT_HEADER,
            text_color=VIBRANT_PRIMARY
        ).pack(side="left")

        # View history button
        history_btn = ModernButton(
            list_header,
            text="📈 View History",
            command=lambda: open_history(),
            width=150,
            height=35
        )
        history_btn.pack(side="right")

        # Students list
        list_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Create scrollable frame for students list
        students_canvas = ctk.CTkCanvas(list_frame, bg=VIBRANT_LIGHT, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(list_frame, orient="vertical", command=students_canvas.yview)
        scrollable_frame = ctk.CTkFrame(students_canvas, fg_color=VIBRANT_LIGHT)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: students_canvas.configure(scrollregion=students_canvas.bbox("all"))
        )

        students_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        students_canvas.configure(yscrollcommand=scrollbar.set)

        students_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def mark_attendance():
            """Mark attendance for the selected section"""
            try:
                section = section_var.get()
                status_label.configure(text="Processing attendance...")
                
                # Mark attendance
                marked_students = facemark_core.mark_attendance(section)
                
                if marked_students:
                    status_label.configure(text=f"Attendance marked for {len(marked_students)} students")
                    display_marked_students(marked_students)
                else:
                    status_label.configure(text="No students were marked present")
                    display_marked_students([])
                    
            except Exception as e:
                status_label.configure(text="Error marking attendance")
                show_error("Attendance Error", str(e))

        def display_marked_students(students):
            """Display the list of marked students"""
            try:
                # Clear existing widgets
                for widget in scrollable_frame.winfo_children():
                    widget.destroy()

                if not students:
                    ctk.CTkLabel(
                        scrollable_frame,
                        text="No students marked present",
                        font=FONT_BODY,
                        text_color=VIBRANT_SECONDARY
                    ).pack(pady=20)
                    return

                # Create header row
                header_frame = ctk.CTkFrame(scrollable_frame, fg_color=VIBRANT_ACCENT, height=40)
                header_frame.pack(fill="x", pady=(0, 10))
                header_frame.pack_propagate(False)

                ctk.CTkLabel(
                    header_frame,
                    text="Name",
                    font=FONT_SMALL,
                    text_color=VIBRANT_LIGHT
                ).pack(side="left", padx=10, pady=10)

                ctk.CTkLabel(
                    header_frame,
                    text="ID",
                    font=FONT_SMALL,
                    text_color=VIBRANT_LIGHT
                ).pack(side="left", padx=10, pady=10)

                ctk.CTkLabel(
                    header_frame,
                    text="Time",
                    font=FONT_SMALL,
                    text_color=VIBRANT_LIGHT
                ).pack(side="right", padx=10, pady=10)

                # Add student rows
                for student in students:
                    student_frame = ctk.CTkFrame(scrollable_frame, fg_color=VIBRANT_BORDER, height=50)
                    student_frame.pack(fill="x", pady=2)
                    student_frame.pack_propagate(False)

                    ctk.CTkLabel(
                        student_frame,
                        text=student['name'],
                        font=FONT_SMALL,
                        text_color=VIBRANT_PRIMARY
                    ).pack(side="left", padx=10, pady=15)

                    ctk.CTkLabel(
                        student_frame,
                        text=student['id'],
                        font=FONT_SMALL,
                        text_color=VIBRANT_PRIMARY
                    ).pack(side="left", padx=10, pady=15)

                    ctk.CTkLabel(
                        student_frame,
                        text=student['time'],
                        font=FONT_SMALL,
                        text_color=VIBRANT_PRIMARY
                    ).pack(side="right", padx=10, pady=15)

            except Exception as e:
                show_error("Error", f"Failed to display marked students: {str(e)}")

        def open_history():
            """Open attendance history"""
            attendance_win.destroy()
            # This will be handled by the main application

        attendance_win.mainloop()
    except Exception as e:
        show_error("Application Error", str(e)) 