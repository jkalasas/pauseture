import tkinter as tk
import cv2
import numpy as np
from tensorflow.keras import models
from PIL import Image, ImageTk
import threading
from config import Settings  # Import Settings class
import time
import pygame  # Import pygame for playing sound
import json
import tkinter.messagebox  # Import messagebox for notifications

class LiveViewPage(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent)
        self.controller = controller
        self.settings = settings  # Use the provided settings instance
        self.label = tk.Label(self)
        self.label.pack()
        self.mymodel = None
        self.videocapture = None
        self.threads = []
        self.bad_posture_start_time = None
        self.good_posture_start_time = None
        self.sound_played = False  # Add a flag to track if sound has been played
        self.watching = False  # Add a flag to track if watching posture
        pygame.mixer.init()  # Initialize pygame mixer
        self.warning_message = None  # Add a reference to the warning message box

        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=10)

        back_button = tk.Button(button_frame, text="Back", command=self.on_back)
        back_button.pack(side="left", padx=5)
        self.stop_music_button = tk.Button(button_frame, text="Stop Music", command=self.stop_music)
        self.stop_music_button.pack(side="left", padx=5)
        self.stop_music_button.pack_forget()  # Hide initially
        self.watch_button = tk.Button(button_frame, text="Start Watching", command=self.toggle_watch)
        self.watch_button.pack(side="left", padx=5)

    def on_back(self):
        self.controller.show_frame("StartPage")
        self.stop_camera()
        self.reset_timers_and_music()

    def start_camera(self):
        self.mymodel = models.load_model(self.settings.model_name)
        self.videocapture = cv2.VideoCapture(0)
        if not self.videocapture.isOpened():
            raise IOError('Cannot open webcam')
        thread = threading.Thread(target=self.update_frame)
        self.threads.append(thread)
        thread.start()

    def stop_camera(self):
        if self.videocapture is not None:
            self.videocapture.release()
            self.videocapture = None

    def stop_music(self):
        pygame.mixer.music.stop()
        self.sound_played = False
        self.stop_music_button.pack_forget()  # Hide the button when music stops

    def reset_timers_and_music(self):
        self.bad_posture_start_time = None
        self.good_posture_start_time = None
        self.stop_music()

    def toggle_watch(self):
        self.watching = not self.watching
        self.watch_button.config(text="Stop Watching" if self.watching else "Start Watching")
        if not self.watching:
            self.reset_timers_and_music()

    def show_warning_message(self):
        if self.warning_message is None:
            self.warning_message = tk.Toplevel(self)
            self.warning_message.title("Posture Alert")
            tk.Label(self.warning_message, text="You have been in bad posture for too long!").pack(pady=10)
            tk.Button(self.warning_message, text="OK", command=self.close_warning_message).pack(pady=5)
            self.warning_message.protocol("WM_DELETE_WINDOW", self.close_warning_message)

    def close_warning_message(self):
        if self.warning_message is not None:
            self.warning_message.destroy()
            self.warning_message = None

    def update_frame(self):
        if self.videocapture is not None:
            _, frame = self.videocapture.read()
            im_color = cv2.flip(frame, flipCode=1)  # flip horizontally
            im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            im = cv2.resize(im, self.settings.image_dimensions)
            im = im / 255  # Normalize the image
            im = im.reshape(1, self.settings.image_dimensions[0], self.settings.image_dimensions[1], 1)
            predictions = self.mymodel.predict(im)
            class_pred = np.argmax(predictions)
            conf = predictions[0][class_pred]
            im_color = cv2.resize(im_color, (800, 480), interpolation=cv2.INTER_AREA)

            if class_pred == 1:
                im_color = cv2.putText(im_color, 'Bad posture', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), thickness=3)
                if self.watching:
                    if self.bad_posture_start_time is None:
                        self.bad_posture_start_time = time.time()
                        self.sound_played = False  # Reset the flag when bad posture is detected
                    elif time.time() - self.bad_posture_start_time > 5:
                        if not self.sound_played or not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load(self.settings.mp3file)
                            pygame.mixer.music.play()
                            self.sound_played = True  # Set the flag to indicate sound has been played
                            self.stop_music_button.pack(side="left", padx=5)  # Show the button when music starts
                            self.focus_force()  # Bring the application window to the front
                            self.show_warning_message()  # Show non-blocking warning message
                    self.good_posture_start_time = None  # Reset good posture timer
            else:
                im_color = cv2.putText(im_color, 'Good posture', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), thickness=2)
                if self.watching:
                    self.bad_posture_start_time = None
                    if self.sound_played:
                        if self.good_posture_start_time is None:
                            self.good_posture_start_time = time.time()
                        elif time.time() - self.good_posture_start_time > 3:
                            self.stop_music()
                            self.good_posture_start_time = None  # Reset good posture timer after stopping music
                    else:
                        self.good_posture_start_time = None
                    if pygame.mixer.music.get_busy():
                        self.stop_music()  # Ensure music stops immediately when good posture is detected
                    if self.warning_message:
                        self.close_warning_message()  # Close the warning message box

            msg = 'Confidence {}%'.format(round(int(conf * 100)))
            im_color = cv2.putText(im_color, msg, (15, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 255), thickness=2)
            im_color = cv2.cvtColor(im_color, cv2.COLOR_BGR2RGB)
            im_pil = Image.fromarray(im_color)  # Convert to PIL image
            img = ImageTk.PhotoImage(image=im_pil)  # Convert to ImageTk
            self.label.imgtk = img
            self.label.configure(image=img)
            self.after(20, self.update_frame)

    def cleanup_threads(self):
        for thread in self.threads:
            if thread.is_alive():
                thread.join()

    def on_close(self):
        self.cleanup_threads()
