import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from config import Settings

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent)
        self.controller = controller
        self.settings = settings
        self.configure(bg="#F5F5F5")  # Match start page background

        # Header
        header_frame = tk.Frame(self, bg="#F5F5F5")
        header_frame.pack(pady=20)
        
        label = tk.Label(header_frame, text="Settings", font=("Helvetica Neue", 18, "bold"), bg="#F5F5F5", fg="#2C3E50")
        label.pack(side="top", fill="x", pady=10)

        # Settings container
        settings_frame = tk.Frame(self, bg="#F5F5F5")
        settings_frame.pack(pady=20, padx=40)

        # Modern styling updates
        label_style = {
            'font': ('Helvetica Neue', 12),
            'bg': "#F5F5F5",
            'fg': '#2C3E50',
            'anchor': 'w'
        }

        entry_style = {
            'font': ('Helvetica Neue', 11),
            'relief': 'solid',
            'bd': 1,
            'width': 25,  # Consistent width
        }

        # Add button style definition
        button_style = {
            'font': ('Helvetica Neue', 12),
            'bd': 0,
            'relief': 'solid',
            'fg': '#2C3E50',
            'bg': 'white',
            'activeforeground': '#2C3E50',
            'borderwidth': 0
        }

        # Create horizontal rows for related settings
        # Row 1: Image Dimensions and Epochs
        row1 = tk.Frame(settings_frame, bg="#F5F5F5")
        row1.pack(fill='x', pady=10)
        
        dim_frame = tk.Frame(row1, bg="#F5F5F5")
        dim_frame.pack(side='left', padx=20)
        tk.Label(dim_frame, text="Image Dimensions:", **label_style).pack(anchor='w')
        self.image_dimensions_entry = tk.Entry(dim_frame, **entry_style)
        self.image_dimensions_entry.pack(pady=5)

        epochs_frame = tk.Frame(row1, bg="#F5F5F5")
        epochs_frame.pack(side='left', padx=20)
        tk.Label(epochs_frame, text="Epochs:", **label_style).pack(anchor='w')
        self.epochs_entry = tk.Entry(epochs_frame, **entry_style)
        self.epochs_entry.pack(pady=5)

        # Row 2: Model Name
        row2 = tk.Frame(settings_frame, bg="#F5F5F5")
        row2.pack(fill='x', pady=10)
        
        model_frame = tk.Frame(row2, bg="#F5F5F5")
        model_frame.pack(anchor='w', padx=20)
        tk.Label(model_frame, text="Model Name:", **label_style).pack(anchor='w')
        self.model_name_entry = tk.Entry(model_frame, **entry_style)
        self.model_name_entry.pack(pady=5)

        # Row 3: Training Directory and MP3 File with Browse buttons
        row3 = tk.Frame(settings_frame, bg="#F5F5F5")
        row3.pack(fill='x', pady=10)

        # Training Directory group
        train_dir_frame = tk.Frame(row3, bg="#F5F5F5")
        train_dir_frame.pack(side='left', padx=20)
        tk.Label(train_dir_frame, text="Training Directory:", **label_style).pack(anchor='w')
        dir_browse_frame = tk.Frame(train_dir_frame, bg="#F5F5F5")
        dir_browse_frame.pack(fill='x')
        self.training_dir_entry = tk.Entry(dir_browse_frame, state='readonly', **entry_style)
        self.training_dir_entry.pack(side='left', pady=5)
        browse_dir_btn = tk.Button(dir_browse_frame, text="Browse", 
            command=self.browse_training_dir,
            **{**button_style, 'width': 8, 'height': 1})
        browse_dir_btn.pack(side='left', padx=5)
        self._apply_button_hover(browse_dir_btn)

        # MP3 File group
        mp3_frame = tk.Frame(row3, bg="#F5F5F5")
        mp3_frame.pack(side='left', padx=20)
        tk.Label(mp3_frame, text="MP3 File:", **label_style).pack(anchor='w')
        mp3_browse_frame = tk.Frame(mp3_frame, bg="#F5F5F5")
        mp3_browse_frame.pack(fill='x')
        self.mp3file_entry = tk.Entry(mp3_browse_frame, state='readonly', **entry_style)
        self.mp3file_entry.pack(side='left', pady=5)
        browse_mp3_btn = tk.Button(mp3_browse_frame, text="Browse", 
            command=self.browse_mp3file,
            **{**button_style, 'width': 8, 'height': 1})
        browse_mp3_btn.pack(side='left', padx=5)
        self._apply_button_hover(browse_mp3_btn)

        # Action buttons at the bottom
        button_container = tk.Frame(self, bg="#F5F5F5")
        button_container.pack(pady=30)

        save_button = tk.Button(button_container, text="Save", command=self.save_settings, **button_style)
        save_button.pack(side='left', padx=10)
        self._apply_button_hover(save_button)

        back_button = tk.Button(button_container, text="Back", 
            command=lambda: controller.show_frame("StartPage"), **button_style)
        back_button.pack(side='left', padx=10)
        self._apply_button_hover(back_button)

        self.load_settings()

    def _apply_button_hover(self, button):
        button.bind('<Enter>', lambda e: self._on_enter(button))
        button.bind('<Leave>', lambda e: self._on_leave(button))

    def _on_enter(self, button):
        """Subtle hover effect"""
        button.configure(
            bg="#000000",
            fg='white',
            font=('Helvetica Neue', 12, 'bold')
        )

    def _on_leave(self, button):
        """Reset button state"""
        button.configure(
            bg='white',
            fg='#2C3E50',
            font=('Helvetica Neue', 12)
        )

    def load_settings(self):
        self.image_dimensions_entry.insert(0, f"{self.settings.image_dimensions[0]},{self.settings.image_dimensions[1]}")
        self.epochs_entry.insert(0, self.settings.epochs)
        self.model_name_entry.insert(0, self.settings.model_name)
        self.training_dir_entry.insert(0, self.settings.training_dir)
        self.mp3file_entry.insert(0, self.settings.mp3file)

    def save_settings(self):
        if not self.validate_settings():
            return
        self.settings.image_dimensions = tuple(map(int, self.image_dimensions_entry.get().split(',')))
        self.settings.epochs = int(self.epochs_entry.get())
        self.settings.model_name = self.model_name_entry.get()
        self.settings.training_dir = self.training_dir_entry.get()
        self.settings.mp3file = self.mp3file_entry.get()
        self.settings.save_settings()
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def validate_settings(self):
        try:
            image_dimensions = tuple(map(int, self.image_dimensions_entry.get().split(',')))
            if len(image_dimensions) != 2 or any (dim <= 0 for dim in image_dimensions):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Image dimensions must be two positive integers separated by a comma.")
            return False

        try:
            epochs = int(self.epochs_entry.get())
            if epochs <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Epochs must be a positive integer.")
            return False

        if not self.model_name_entry.get().strip():
            messagebox.showerror("Invalid Input", "Model name cannot be empty.")
            return False

        if not self.training_dir_entry.get().strip():
            messagebox.showerror("Invalid Input", "Training directory cannot be empty.")
            return False

        if not self.mp3file_entry.get().strip():
            messagebox.showerror("Invalid Input", "MP3 file cannot be empty.")
            return False

        return True

    def browse_mp3file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if file_path:
            self.mp3file_entry.configure(state='normal')  # Temporarily enable entry
            self.mp3file_entry.delete(0, tk.END)
            self.mp3file_entry.insert(0, file_path)
            self.mp3file_entry.configure(state='readonly')  # Set back to readonly

    def browse_training_dir(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.training_dir_entry.configure(state='normal')  # Temporarily enable entry
            self.training_dir_entry.delete(0, tk.END)
            self.training_dir_entry.insert(0, folder_path)
            self.training_dir_entry.configure(state='readonly')  # Set back to readonly
