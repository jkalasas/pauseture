import tkinter as tk
from pages import StartPage, LiveViewPage, TrainingPage, SettingsPage  # Import the pages
from config import Settings  # Import Settings

class PostureApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pauseture")
        self.geometry("800x600")
        self.frames = {}
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.settings = Settings()  # Create an instance of Settings

        for F in (StartPage, LiveViewPage, TrainingPage, SettingsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self, settings=self.settings)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        self.settings.load_settings()  # Reload settings
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "LiveViewPage":
            frame.start_camera()
        else:
            if hasattr(frame, 'stop_camera'):
                frame.stop_camera()

    def on_close(self):
        for frame in self.frames.values():
            if hasattr(frame, 'on_close'):
                frame.on_close()
        self.destroy()

if __name__ == "__main__":
    app = PostureApp()
    app.mainloop()
