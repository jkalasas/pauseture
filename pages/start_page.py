import tkinter as tk
import os
from config import Settings  # Import Settings class

class StartPage(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent)
        self.controller = controller
        self.settings = settings  # Use the provided settings instance
        label = tk.Label(self, text="Posture Watch", font=("Helvetica", 18, "bold"))
        label.pack(side="top", fill="x", pady=10)
        live_view_button = tk.Button(self, text="Live View", command=self.check_model_and_show_live_view)
        live_view_button.pack(pady=5)
        training_button = tk.Button(self, text="Training", command=lambda: controller.show_frame("TrainingPage"))
        training_button.pack(pady=5)
        settings_button = tk.Button(self, text="Settings", command=lambda: controller.show_frame("SettingsPage"))
        settings_button.pack(pady=5)

    def check_model_and_show_live_view(self):
        if os.path.exists(self.settings.model_name):
            self.controller.show_frame("LiveViewPage")
        else:
            tk.messagebox.showerror("Error", "No trained model found. Please train the model first.")

    def start_camera(self):
        pass

    def stop_camera(self):
        pass
