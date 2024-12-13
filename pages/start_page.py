import tkinter as tk
import os
from config import Settings  # Import Settings class
class StartPage(tk.Frame):
    def __init__(self, parent, controller, settings):
        super().__init__(parent)
        self.controller = controller
        self.settings = settings
        self.configure(bg="#F5F5F5")  # Light, clean background

        # Create a modern header
        header_frame = tk.Frame(self, bg="#F5F5F5")
        header_frame.pack(pady=20, expand=True)  # Reduced from 40 to 20

        # Clean, professional title
        logo_alt_path = os.path.join("assets", "logo-alt.png")
        logo_alt_image = tk.PhotoImage(file=logo_alt_path)
        # Subsample if needed to adjust size
        small_logo_alt = logo_alt_image.subsample(2, 2)  # Adjust subsample values as needed
        self.title_label = tk.Label(header_frame, image=small_logo_alt, bg="#F5F5F5")
        self.title_label.image = small_logo_alt  # Keep reference
        self.title_label.pack()

        # Main menu container - no vertical padding
        menu_frame = tk.Frame(self, bg="#F5F5F5")
        menu_frame.pack(pady=40)  # Increased padding to 20

        # Modern button design
        button_style = {
            'font': ('Helvetica Neue', 12),
            'width': 15,
            'height': 2,
            'bd': 0,
            'relief': 'solid',
            'fg': '#2C3E50',
            'activeforeground': '#2C3E50',
            'borderwidth': 0
        }

        # Create horizontal container for buttons
        button_container = tk.Frame(menu_frame, bg="#F5F5F5")
        button_container.pack(expand=True)

        # Clean, minimal buttons
        buttons_data = [
            ("Start Monitoring", "#000000", self.check_model_and_show_live_view),
            ("Training Mode", "#000000", lambda: controller.show_frame("TrainingPage")),
            ("Settings", "#000000", lambda: controller.show_frame("SettingsPage"))
        ]

        for text, color, command in buttons_data:
            btn_frame = tk.Frame(button_container, bg="#F5F5F5")
            btn_frame.pack(side=tk.LEFT, padx=10)
            
            btn = tk.Button(btn_frame, text=text, bg="white",
              command=command, **button_style)
            btn.pack(pady=5)
            
            btn.config(highlightthickness=0)
            btn['relief'] = 'groove'
            
            def make_enter_handler(b, c):
                def handler(_):
                    self._on_enter(b, c)
                return handler
            
            def make_leave_handler(b):
                def handler(_):
                    self._on_leave(b)
                return handler
            
            btn.bind('<Enter>', make_enter_handler(btn, color))
            btn.bind('<Leave>', make_leave_handler(btn))

        # Show the logo initially
        self.show_and_fade_logo()

  

    def _on_enter(self, button, color):
        """Subtle hover effect"""
        button.configure(
            bg=color,
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
    def show_and_fade_logo(self):
        """Shows logo and fades it out before showing main menu"""
        # Create logo container
        self.logo_frame = tk.Frame(self, bg="#F5F5F5")
        self.logo_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Load and display logo
        logo_path = os.path.join("assets", "logo.png")
        logo_image = tk.PhotoImage(file=logo_path)
        # Subsample the image to make it smaller (2 means half size, 3 means one-third, etc.)
        small_logo = logo_image.subsample(1, 1)
        self.logo_label = tk.Label(self.logo_frame, image=small_logo, bg="#F5F5F5")
        self.logo_label.image = small_logo  # Keep reference
        self.logo_label.pack()
        
        # Start fade out after 2 seconds
        self.after(2000, self.fade_logo)

    def fade_logo(self):
        """Gradually fades out the logo by reducing opacity"""
        opacity = getattr(self, '_opacity', 0)  # Start from 0 (white)
        if opacity < 255:  # Go up to 255 (transparent)
            opacity = min(255, opacity + 15)
            self._opacity = opacity
            # Create white background that becomes more transparent
            self.logo_label.configure(bg=f'#FFFFFF')
            self.logo_frame.configure(bg=f'#{opacity:02x}{opacity:02x}{opacity:02x}')
            self.after(50, self.fade_logo)
        else:
            self.logo_frame.destroy()
            self.show_main_menu()

    def show_main_menu(self):
        """Shows the main menu after logo fades"""
        self.title_label.pack()

    def check_model_and_show_live_view(self):
        if os.path.exists(self.settings.model_name):
            self.controller.show_frame("LiveViewPage")
        else:
            tk.messagebox.showerror("System Error", "⚠️ No trained model detected\nInitiate training sequence first")

    def start_camera(self):
        pass

    def stop_camera(self):
        pass
