import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from config import Settings

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent)
        self.controller = controller
        self.settings = settings  # Use the provided settings instance
        label = tk.Label(self, text="Settings", font=("Helvetica", 18, "bold"))
        label.pack(side="top", fill="x", pady=10)

        self.image_dimensions_label = tk.Label(self, text="Image Dimensions (width, height):")
        self.image_dimensions_label.pack(pady=5)
        self.image_dimensions_entry = tk.Entry(self)
        self.image_dimensions_entry.pack(pady=5)

        self.epochs_label = tk.Label(self, text="Epochs:")
        self.epochs_label.pack(pady=5)
        self.epochs_entry = tk.Entry(self)
        self.epochs_entry.pack(pady=5)

        self.model_name_label = tk.Label(self, text="Model Name:")
        self.model_name_label.pack(pady=5)
        self.model_name_entry = tk.Entry(self)
        self.model_name_entry.pack(pady=5)

        self.training_dir_label = tk.Label(self, text="Training Directory:")
        self.training_dir_label.pack(pady=5)
        self.training_dir_entry = tk.Entry(self, state='readonly')
        self.training_dir_entry.pack(pady=5)
        self.training_dir_button = tk.Button(self, text="Browse", command=self.browse_training_dir)
        self.training_dir_button.pack(pady=5)

        self.mp3file_label = tk.Label(self, text="MP3 File:")
        self.mp3file_label.pack(pady=5)
        self.mp3file_entry = tk.Entry(self, state='readonly')
        self.mp3file_entry.pack(pady=5)
        self.mp3file_button = tk.Button(self, text="Browse", command=self.browse_mp3file)
        self.mp3file_button.pack(pady=5)

        save_button = tk.Button(self, text="Save", command=self.save_settings)
        save_button.pack(pady=10)

        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("StartPage"))
        back_button.pack(pady=10)

        self.load_settings()

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
            self.mp3file_entry.delete(0, tk.END)
            self.mp3file_entry.insert(0, file_path)

    def browse_training_dir(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.training_dir_entry.delete(0, tk.END)
            self.training_dir_entry.insert(0, folder_path)
