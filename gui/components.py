# components.py - Reusable UI components

import customtkinter as ctk
from .styles import *

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
            font=FONT_SUBHEADER,
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
            kwargs['font'] = FONT_BUTTON
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
            font=FONT_SMALL,
            **kwargs
        ) 