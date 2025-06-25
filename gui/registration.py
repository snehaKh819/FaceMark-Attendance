# registration.py - Student registration functionality

import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
import os
from .styles import *
from .components import ModernButton, ModernEntry

def show_error(title, message):
    """Show error message with traceback in development"""
    import traceback
    error_msg = f"{message}\n\nTraceback:\n{traceback.format_exc()}"
    messagebox.showerror(title, error_msg)

def show_registration(session, facemark_core):
    """Display the registration screen"""
    try:
        reg_win = ctk.CTk()
        reg_win.title("FaceMark - Student Registration")
        reg_win.state("zoomed")
        reg_win.resizable(False, False)
        reg_win.minsize(1200, 800)

        # Main container
        main_container = ctk.CTkFrame(reg_win, fg_color=VIBRANT_BG)
        main_container.pack(fill="both", expand=True)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color=VIBRANT_LIGHT, height=100)
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)

        ctk.CTkLabel(
            header_frame,
            text="📝 Student Registration",
            font=FONT_TITLE,
            text_color=VIBRANT_PRIMARY
        ).pack(side="left", padx=30, pady=30)

        # Back button
        back_btn = ModernButton(
            header_frame,
            text="← Back to Home",
            command=reg_win.destroy,
            width=150,
            height=40
        )
        back_btn.pack(side="right", padx=30, pady=30)

        # Content area
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left panel - Registration form
        left_panel = ctk.CTkFrame(content_frame, fg_color=VIBRANT_LIGHT)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Form title
        ctk.CTkLabel(
            left_panel,
            text="Register New Student",
            font=FONT_HEADER,
            text_color=VIBRANT_PRIMARY
        ).pack(pady=20)

        # Form fields
        form_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Student name
        name_label = ctk.CTkLabel(
            form_frame,
            text="👤 Student Name",
            font=FONT_SMALL,
            text_color=VIBRANT_PRIMARY,
            anchor="w"
        )
        name_label.pack(fill="x", pady=(0, 5))

        name_var = tk.StringVar()
        name_entry = ModernEntry(
            form_frame,
            textvariable=name_var,
            placeholder_text="Enter student's full name",
            height=45
        )
        name_entry.pack(fill="x", pady=(0, 15))

        # Student ID
        id_label = ctk.CTkLabel(
            form_frame,
            text="🆔 Student ID",
            font=FONT_SMALL,
            text_color=VIBRANT_PRIMARY,
            anchor="w"
        )
        id_label.pack(fill="x", pady=(0, 5))

        id_var = tk.StringVar()
        id_entry = ModernEntry(
            form_frame,
            textvariable=id_var,
            placeholder_text="Enter student ID",
            height=45
        )
        id_entry.pack(fill="x", pady=(0, 15))

        # Section selection
        section_label = ctk.CTkLabel(
            form_frame,
            text="📚 Section",
            font=FONT_SMALL,
            text_color=VIBRANT_PRIMARY,
            anchor="w"
        )
        section_label.pack(fill="x", pady=(0, 5))

        section_var = tk.StringVar(value="A")
        section_menu = ctk.CTkOptionMenu(
            form_frame,
            values=SECTIONS,
            variable=section_var,
            fg_color=VIBRANT_LIGHT,
            button_color=VIBRANT_ACCENT,
            button_hover_color=VIBRANT_HOVER,
            text_color=VIBRANT_TEXT,
            font=FONT_SMALL,
            height=45
        )
        section_menu.pack(fill="x", pady=(0, 15))

        # Image folder selection
        folder_label = ctk.CTkLabel(
            form_frame,
            text="📁 Image Folder",
            font=FONT_SMALL,
            text_color=VIBRANT_PRIMARY,
            anchor="w"
        )
        folder_label.pack(fill="x", pady=(0, 5))

        folder_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        folder_frame.pack(fill="x", pady=(0, 15))

        folder_var = tk.StringVar()
        folder_entry = ModernEntry(
            folder_frame,
            textvariable=folder_var,
            placeholder_text="Select folder with student images",
            height=45
        )
        folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def browse_folder():
            folder = filedialog.askdirectory()
            if folder:
                folder_var.set(folder)

        browse_btn = ModernButton(
            folder_frame,
            text="Browse",
            command=browse_folder,
            width=100,
            height=45
        )
        browse_btn.pack(side="right")

        # Register button
        register_btn = ModernButton(
            form_frame,
            text="Register Student",
            command=lambda: register_student(),
            height=50,
            font=FONT_BUTTON
        )
        register_btn.pack(fill="x", pady=(20, 0))

        # Right panel - Registered students list
        right_panel = ctk.CTkFrame(content_frame, fg_color=VIBRANT_LIGHT)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # List title
        list_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        list_header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            list_header,
            text="Registered Students",
            font=FONT_HEADER,
            text_color=VIBRANT_PRIMARY
        ).pack(side="left")

        # Refresh button
        refresh_btn = ModernButton(
            list_header,
            text="🔄 Refresh",
            command=lambda: refresh_students_list(),
            width=120,
            height=35
        )
        refresh_btn.pack(side="right")

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

        def refresh_students_list():
            """Refresh the students list"""
            try:
                # Clear existing widgets
                for widget in scrollable_frame.winfo_children():
                    widget.destroy()

                # Get registered students
                students = facemark_core.get_registered_students()
                
                if not students:
                    ctk.CTkLabel(
                        scrollable_frame,
                        text="No students registered yet",
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
                    text="Section",
                    font=FONT_SMALL,
                    text_color=VIBRANT_LIGHT
                ).pack(side="left", padx=10, pady=10)

                ctk.CTkLabel(
                    header_frame,
                    text="Action",
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
                        text=student['section'],
                        font=FONT_SMALL,
                        text_color=VIBRANT_PRIMARY
                    ).pack(side="left", padx=10, pady=15)

                    # Delete button
                    delete_btn = ModernButton(
                        student_frame,
                        text="🗑️",
                        command=lambda s=student: delete_student(s),
                        width=50,
                        height=30,
                        font=FONT_SMALL,
                        fg_color=VIBRANT_WARNING,
                        hover_color="#E17055"
                    )
                    delete_btn.pack(side="right", padx=10, pady=10)

            except Exception as e:
                show_error("Error", f"Failed to refresh students list: {str(e)}")

        def delete_student(student):
            """Delete a student"""
            try:
                result = messagebox.askyesno(
                    "Confirm Delete",
                    f"Are you sure you want to delete {student['name']} (ID: {student['id']})?"
                )
                if result:
                    facemark_core.delete_student(student['name'], student['section'])
                    messagebox.showinfo("Success", f"Student {student['name']} deleted successfully!")
                    refresh_students_list()
            except Exception as e:
                show_error("Error", f"Failed to delete student: {str(e)}")

        def register_student():
            """Register a new student"""
            try:
                name = name_var.get().strip()
                student_id = id_var.get().strip()
                section = section_var.get()
                folder_path = folder_var.get().strip()

                if not name or not student_id or not folder_path:
                    messagebox.showwarning("Input Error", "Please fill in all fields.")
                    return

                if not os.path.exists(folder_path):
                    messagebox.showerror("Error", "Selected folder does not exist.")
                    return

                # Register the student
                facemark_core.register_student(name, student_id, section, folder_path)
                
                messagebox.showinfo("Success", f"Student {name} registered successfully!")
                
                # Clear form
                name_var.set("")
                id_var.set("")
                folder_var.set("")
                
                # Refresh students list
                refresh_students_list()

            except Exception as e:
                show_error("Registration Error", str(e))

        # Initial load of students list
        refresh_students_list()

        reg_win.mainloop()
    except Exception as e:
        show_error("Application Error", str(e)) 