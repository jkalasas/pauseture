import tkinter as tk
from tkinter import messagebox
import threading
import cv2
import os
import numpy as np
from tensorflow.keras import layers, models
from sklearn.utils import class_weight
from pathlib import Path
from PIL import Image, ImageTk
from config import Settings  # Import necessary functions and variables
import json

class TrainingPage(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent)
        self.controller = controller
        self.settings = settings  # Use the provided settings instance
        label = tk.Label(self, text="Training Page", font=("Helvetica", 18, "bold"))
        label.pack(side="top", fill="x", pady=10)

        self.label = tk.Label(self)
        self.label.pack()

        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=10)

        self.capture_good_button = tk.Button(button_frame, text="Capture Good Posture", command=self.capture_good_posture)
        self.capture_good_button.pack(side="left", padx=5)

        self.capture_bad_button = tk.Button(button_frame, text="Capture Bad Posture", command=self.capture_bad_posture)
        self.capture_bad_button.pack(side="left", padx=5)

        self.train_button = tk.Button(button_frame, text="Train Model", command=self.train_model)
        self.train_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Capture", command=self.stop_capture)
        self.stop_button.pack(side="left", padx=5)
        self.stop_button.pack_forget()  # Hide initially

        self.back_button = tk.Button(button_frame, text="Back", command=lambda: controller.show_frame("StartPage"))
        self.back_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear Images", command=self.clear_images)
        self.clear_button.pack(side="left", padx=5)

        self.progress_label = tk.Label(self, text="")
        self.progress_label.pack(side="top", fill="x", pady=5)

        self.good_image_count = len(os.listdir(f'{self.settings.training_dir}/action_01')) if os.path.exists(f'{self.settings.training_dir}/action_01') else 0
        self.bad_image_count = len(os.listdir(f'{self.settings.training_dir}/action_02')) if os.path.exists(f'{self.settings.training_dir}/action_02') else 0

        self.good_count_label = tk.Label(self, text=f"Good Posture Images: {self.good_image_count}")
        self.good_count_label.pack(side="top", fill="x", pady=5)

        self.bad_count_label = tk.Label(self, text=f"Bad Posture Images: {self.bad_image_count}")
        self.bad_count_label.pack(side="top", fill="x", pady=5)

        self.videocapture = None
        self.capturing = False

        self.placeholder_image = ImageTk.PhotoImage(Image.new('RGB', self.settings.image_dimensions, color='gray'))
        self.label.configure(image=self.placeholder_image)

        self.threads = []
        self.stop_event = threading.Event()

    def start_camera(self):
        pass

    def stop_camera(self):
        if self.videocapture is not None:
            self.videocapture.release()
            self.videocapture = None

    def capture_good_posture(self):
        self.capturing = True
        self.disable_buttons()
        self.stop_button.pack(side="left", padx=5)  # Show stop button
        thread = threading.Thread(target=self.do_capture_action, args=(1, 'Good'))
        self.threads.append(thread)
        thread.start()

    def capture_bad_posture(self):
        self.capturing = True
        self.disable_buttons()
        self.stop_button.pack(side="left", padx=5)  # Show stop button
        thread = threading.Thread(target=self.do_capture_action, args=(2, 'Bad'))
        self.threads.append(thread)
        thread.start()

    def stop_capture(self):
        self.capturing = False
        self.enable_buttons()
        self.stop_button.pack_forget()  # Hide stop button
        self.stop_camera()
        self.label.configure(image=self.placeholder_image)

    def disable_buttons(self):
        self.capture_good_button.config(state=tk.DISABLED)
        self.capture_bad_button.config(state=tk.DISABLED)
        self.train_button.config(state=tk.DISABLED)
        self.back_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.capture_good_button.config(state=tk.NORMAL)
        self.capture_bad_button.config(state=tk.NORMAL)
        self.train_button.config(state=tk.NORMAL)
        self.back_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)

    def train_model(self):
        self.disable_buttons()
        self.progress_label.config(text="Training in progress...")
        self.stop_event.clear()
        thread = threading.Thread(target=self._train_model)
        self.threads.append(thread)
        thread.start()

    def do_capture_action(self, action_n, action_label):
        img_count = 0
        output_folder = f'{self.settings.training_dir}/action_{action_n:02}'
        print(f'Capturing samples for {action_label} into folder {output_folder}')
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        self.videocapture = cv2.VideoCapture(0)
        if not self.videocapture.isOpened():
            raise IOError('Cannot open webcam')

        self.update_frame(action_n, output_folder, img_count)

    def update_frame(self, action_n, output_folder, img_count):
        if self.videocapture is not None and self.capturing:
            _, frame = self.videocapture.read()
            filename = f'{output_folder}/{img_count:08}.png'
            cv2.imwrite(filename, frame)
            img_count += 1

            if action_n == 1:
                self.good_image_count += 1
                self.good_count_label.config(text=f"Good Posture Images: {self.good_image_count}")
            elif action_n == 2:
                self.bad_image_count += 1
                self.bad_count_label.config(text=f"Bad Posture Images: {self.bad_image_count}")

            im_color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im_pil = Image.fromarray(im_color)
            img = ImageTk.PhotoImage(image=im_pil)
            self.label.imgtk = img
            self.label.configure(image=img)

            cv2.waitKey(1000)
            self.after(20, self.update_frame, action_n, output_folder, img_count)

    def _train_model(self):
        train_images = []
        train_labels = []
        class_folders = os.listdir(self.settings.training_dir)

        class_label_indexer = 0
        for c in class_folders:
            print(f'Training with class {c}')
            for f in os.listdir(f'{self.settings.training_dir}/{c}'):
                im = cv2.imread(f'{self.settings.training_dir}/{c}/{f}', 0)
                im = cv2.resize(im, self.settings.image_dimensions)
                train_images.append(im)
                train_labels.append(class_label_indexer)
            class_label_indexer += 1

        train_images = np.array(train_images)
        train_labels = np.array(train_labels)

        indices = np.arange(train_labels.shape[0])
        np.random.shuffle(indices)
        train_images = train_images[indices]
        train_labels = train_labels[indices]
        train_images = train_images / 255  # Normalize image
        n = len(train_images)
        train_images = train_images.reshape(n, self.settings.image_dimensions[0], self.settings.image_dimensions[1], 1)

        class_weights = class_weight.compute_class_weight('balanced', np.unique(train_labels), train_labels)
        class_weights_dict = {i: class_weights[i] for i in range(len(class_weights))}
        model = models.Sequential()
        model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(self.settings.image_dimensions[0], self.settings.image_dimensions[1], 1)))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.add(layers.Flatten())
        model.add(layers.Dense(64, activation='relu'))
        model.add(layers.Dense(len(class_folders), activation='softmax'))
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        for epoch in range(self.settings.epochs):
            if self.stop_event.is_set():
                break
            model.fit(train_images, train_labels, epochs=1, class_weight=class_weights_dict)
        model.save(self.settings.model_name)
        self.progress_label.config(text="Training completed successfully!")
        self.enable_buttons()
        messagebox.showinfo("Training", "Model training completed successfully!")

    def clear_images(self):
        if messagebox.askyesno("Clear Images", "Are you sure you want to clear all captured images?"):
            for folder in ['action_01', 'action_02']:
                folder_path = f'{self.settings.training_dir}/{folder}'
                if os.path.exists(folder_path):
                    for file in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
            self.good_image_count = 0
            self.bad_image_count = 0
            self.good_count_label.config(text="Good Posture Images: 0")
            self.bad_count_label.config(text="Bad Posture Images: 0")
            messagebox.showinfo("Clear Images", "All captured images have been cleared.")

    def cleanup_threads(self):
        self.stop_event.set()
        for thread in self.threads:
            if thread.is_alive():
                thread.join()

    def on_close(self):
        self.cleanup_threads()
