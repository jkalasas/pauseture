import json

class Settings:
    def __init__(self):
        self.image_dimensions = (224, 224)
        self.epochs = 10
        self.model_name = 'posture_model.h5'
        self.training_dir = 'train'
        self.mp3file = 'default.mp3'
        self.load_settings()

    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                self.image_dimensions = tuple(settings.get('image_dimensions', self.image_dimensions))
                self.epochs = settings.get('epochs', self.epochs)
                self.model_name = settings.get('model_name', self.model_name)
                self.training_dir = settings.get('training_dir', self.training_dir)
                self.mp3file = settings.get('mp3file', self.mp3file)
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {
            "image_dimensions": self.image_dimensions,
            "epochs": self.epochs,
            "model_name": self.model_name,
            "training_dir": self.training_dir,
            "mp3file": self.mp3file
        }
        with open("settings.json", "w") as file:
            json.dump(settings, file)
