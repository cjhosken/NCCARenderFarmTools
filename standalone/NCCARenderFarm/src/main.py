import sys
import os
from PIL import Image, ImageTk
from tkinter import Tk, ttk, Toplevel, Frame, LEFT, RIGHT, PhotoImage, messagebox

from utils import get_os_type, get_renderfarm
from browser import NCCA_RenderFarm_Browser
from renderfarm import InvalidCredentialsException, ConnectionFailedException
from dotenv import load_dotenv

class NCCARenderFarmApplication():
    
    def __init__(self) -> None:
        self.root = Tk()
        self.root.withdraw()
        self.os = get_os_type()
        self.application_folder = os.path.dirname(os.path.dirname(__file__))

        self.set_application_icon()
        
        if self.os == "other":
            raise Exception("Current operating system not supported.")
        
        env_path = os.path.join(self.application_folder, ".env")
        use_env = False
        
        if os.path.exists(env_path) and use_env:
            try:
                load_dotenv(env_path)
                self.username = os.getenv('USERNAME')
                self.password = os.getenv('PASSWORD')
            
                self.renderfarm = get_renderfarm(self.username, self.password)

                if self.renderfarm is not None:
                    self.initialize_main_window()
                else:
                    self.show_error_and_quit("Connection Failed", "Failed to connect to the render farm.")
            except InvalidCredentialsException:
                self.show_error_and_quit("Invalid Credentials", "The provided credentials are invalid.")
            except ConnectionFailedException:
                self.show_error_and_quit("Connection Failed", "Failed to connect to the render farm.")
            except Exception as e:
                self.show_error_and_quit("Error", str(e))
        else:
            self.create_sign_in_window()

    def set_application_icon(self):
        icon_path = os.path.join(self.application_folder, "assets/icons/ncca_render_farm.png")
        if os.path.exists(icon_path):
            self.root.iconphoto(True, PhotoImage(file=icon_path))
        else:
            print("Application icon not found.")

        

    def create_sign_in_window(self):
        self.sign_in_window = Toplevel(self.root)
        self.sign_in_window.configure()
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
        main_frame = Frame(self.sign_in_window)
        main_frame.pack(expand=True, fill="both")

        # Error message label
        self.sign_in_error_label = ttk.Label(main_frame, text="")
        self.sign_in_error_label.configure(foreground="red", font=('Helvetica', 10))
        self.sign_in_error_label.pack(pady=(10, 5))

        # Username Label and Entry
        username_frame = Frame(main_frame, width=200)
        username_frame.pack(pady=(5, 5), fill="both", expand=False)

        username_label = ttk.Label(username_frame, text="Username:")
        username_label.pack(side=LEFT, padx=(100, 5))

        def validate_input(new_text):
            return len(new_text) <= 10

        username_validation = self.root.register(validate_input)

        self.username_entry = ttk.Entry(username_frame, style="TEntry", validate="key", validatecommand=(username_validation, "%P"))
        self.username_entry.pack(side=RIGHT, fill="x", expand=True, padx=(5, 100))
        self.username_entry.config(font=('Helvetica', 15))

        # Password Label and Entry
        password_frame = Frame(main_frame, width=200)
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
                self.sign_in_error_label.configure(text="Failed to connect to the render farm.")
        except InvalidCredentialsException:
            self.sign_in_error_label.configure(text="Invalid username or password. Please try again.")
        except ConnectionFailedException:
            self.show_sign_in_error("The NCCA Renderfarm can't be accessed. Please try again later.")
        except Exception as e:
            self.show_error_and_quit("Error", str(e))

    def show_sign_in_error(self, error_message):
        # Clear the input fields
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')

        # Remove any existing children from the sign_in_window
        for widget in self.sign_in_window.winfo_children():
            widget.destroy()

        # Create the error label
        error_label_text = error_message
        error_label = ttk.Label(self.sign_in_window, text=error_label_text, wraplength=400, anchor="center", justify="center")
        error_label.pack(pady=(20, 0))

        error_image_path = os.path.join(self.application_folder, "assets/images/sad_frog.jpg")  # Change this to the actual path of your error image
        if os.path.exists(error_image_path):
            error_image = Image.open(error_image_path)
            error_image = error_image.resize((150, 150), Image.ADAPTIVE)  # Adjust the size as needed
            error_image = ImageTk.PhotoImage(error_image)

            error_image_label = ttk.Label(self.sign_in_window, image=error_image)
            error_image_label.image = error_image  # Keep a reference to avoid garbage collection
            error_image_label.pack(pady=0)
        else:
            print("Error image not found.")

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

    def show_error_and_quit(self, title, message):
        messagebox.showerror(title, message)
        self.quit()

def main():
    app = NCCARenderFarmApplication()
    app.start()

if __name__ == "__main__":
    main()
