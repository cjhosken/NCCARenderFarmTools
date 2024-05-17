import sys
import os
from PIL import Image, ImageTk
from tkinter import Tk, ttk, Toplevel, Frame, LEFT, RIGHT, PhotoImage

from utils import get_os_type, get_renderfarm
from browser import NCCA_RenderFarm_Browser

class NCCARenderFarmApplication():
    
    def __init__(self) -> None:
        self.root = Tk()

        self.root.withdraw()
        self.sign_in_window = Toplevel(self.root)
        self.os = get_os_type()
        self.application_folder = os.path.dirname(os.path.dirname(__file__))

        self.set_application_icon()
        
        if (os == "other"):
            raise Exception("Current operating system not supported.")
        
        self.configure_styles()
        self.create_sign_in_window()

    def set_application_icon(self):
            icon_path = os.path.join(self.application_folder, "assets/icons/ncca_render_farm.png")
            if os.path.exists(icon_path):
                self.root.iconphoto(True, PhotoImage(file=icon_path))
            else:
                print("Application icon not found.")

        
    def configure_styles(self):
        self.style = ttk.Style()

        # Configure the root theme
        self.style.theme_use('clam')

        # Configure the colors
        self.style.configure('.', background='#FFFFFF', foreground='#000000')  # Set background to white and foreground (text) to black
        self.style.configure('TButton', background='#000000', foreground='#FFFFFF', bordercolor='none', borderwidth=1, padding=(10, 10), font=('Helvetica', 15), width=20)  # Set button properties
        self.style.map('TButton', background=[('active', '#FFFFFF')], bordercolor=[("active", "black")], foreground=[('active', "#000000")])  # Change button background color on active state

        self.style.configure('TLabel', font=('Helvetica', 15))
        

    def create_sign_in_window(self):
        self.sign_in_window.configure(background="white")
        self.sign_in_window.title("NCCA RenderFarm Sign-In")

        # Get window dimensions
        window_width = 500
        window_height = 200
        screen_width = self.sign_in_window.winfo_screenwidth()
        screen_height = self.sign_in_window.winfo_screenheight()

        # Calculate centered position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set window geometry
        self.sign_in_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.sign_in_window.resizable(False, False)
        self.sign_in_window.protocol("WM_DELETE_WINDOW", self.quit)

        # Main frame to center the interface vertically
        main_frame = Frame(self.sign_in_window, background="white")
        main_frame.pack(expand=True, fill="both")

        # Error message label
        self.sign_in_error_label = ttk.Label(main_frame, text="")
        self.sign_in_error_label.configure(foreground="red", font=('Helvetica', 10))
        self.sign_in_error_label.pack(pady=(10, 5))

        # Username Label and Entry
        username_frame = Frame(main_frame, background="white", width=200)
        username_frame.pack(pady=(5, 5), fill="both", expand=False)

        username_label = ttk.Label(username_frame, text="Username:")
        username_label.pack(side=LEFT, padx=(100, 5))

        def validate_input(new_text):
            return len(new_text) <= 8

        username_validation = self.root.register(validate_input)

        self.username_entry = ttk.Entry(username_frame, style="TEntry", validate="key", validatecommand=(username_validation, "%P"))
        self.username_entry.pack(side=RIGHT, fill="x", expand=True, padx=(5, 100))
        self.username_entry.config(font=('Helvetica', 15))

        # Password Label and Entry
        password_frame = Frame(main_frame, background="white", width=200)
        password_frame.pack(pady=(5, 5), fill="both", expand=True)

        password_label = ttk.Label(password_frame, text="Password:")
        password_label.pack(side=LEFT, padx=(100, 5))

        self.password_entry = ttk.Entry(password_frame, show="*", style="TEntry")
        self.password_entry.pack(side=RIGHT, fill="x", expand=True, padx=(5, 100))
        self.password_entry.config(font=('Helvetica', 15))

        # Sign In Button
        sign_in_button = ttk.Button(main_frame, text="Sign In", command=self.sign_in, style="TButton", padding=(5, 5))
        sign_in_button.configure(cursor="hand2")
        sign_in_button.pack(pady=20, expand=True)

    
    def sign_in(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            self.renderfarm = get_renderfarm(username, password)
            if self.renderfarm is not None:
                self.username = username
                self.sign_in_window.destroy()
                self.initialize_main_window()
            else:
                self.sign_in_error_label.configure(text="Invalid username or password. Please try again.")
        except Exception as e:
            # Clear the input fields
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            
            # Remove any existing children from the sign_in_window
            for widget in self.sign_in_window.winfo_children():
                widget.destroy()
            
            # Create the error label
            error_label_text = "The NCCA Renderfarm can't be accessed. Please try again later."
            error_label = ttk.Label(self.sign_in_window, text=error_label_text, wraplength=400, anchor="center", justify="center")
            error_label.pack(pady=(20, 0))

            error_image_path = os.path.join(self.application_folder, "assets/images/sad_frog.jpg")  # Change this to the actual path of your error image
            error_image = Image.open(error_image_path)
            error_image = error_image.resize((150, 150), Image.ADAPTIVE)  # Adjust the size as needed
            error_image = ImageTk.PhotoImage(error_image)

            error_image_label = ttk.Label(self.sign_in_window, image=error_image)
            error_image_label.image = error_image  # Keep a reference to avoid garbage collection
            error_image_label.pack(pady=0)


    def initialize_main_window(self):
        self.root.deiconify()
        self.root.title("NCCA Render Farm")

        icon_folder = os.path.join(self.application_folder, "assets/icons/")
        NCCA_RenderFarm_Browser(self.root, self.username, self.renderfarm, icon_folder, 16)

    def start(self):
        self.root.mainloop()

    def quit(self):
        self.root.destroy()
        sys.exit()

def main():
    app = NCCARenderFarmApplication()
    app.start()

if __name__ == "__main__":
    main()