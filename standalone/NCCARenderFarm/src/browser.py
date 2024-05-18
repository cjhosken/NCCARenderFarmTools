import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk, Menu, filedialog
from PIL import Image, ImageTk
import os
from utils import get_user_name


class NCCA_RenderFarm_Browser():
    def __init__(self, root, username, renderfarm, icon_folder, icon_size=16) -> None:
        self.root = root
        self.username = username
        self.renderfarm = renderfarm

        self.FILE_ICON = ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "text-x-generic.png")).resize((icon_size, icon_size), Image.ADAPTIVE))
        self.FOLDER_ICON = ImageTk.PhotoImage(Image.open(os.path.join(icon_folder,"folder.png")).resize((icon_size, icon_size), Image.ADAPTIVE))

        self.IMAGE_ICON = ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "image-x-generic.png")).resize((icon_size, icon_size), Image.ADAPTIVE))
        self.HOUDINI_ICON = ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "houdini.png")).resize((icon_size, icon_size), Image.ADAPTIVE))
        self.MAYA_ICON = ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "maya.png")).resize((icon_size, icon_size), Image.ADAPTIVE))
        self.BLENDER_ICON = ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "blender.png")).resize((icon_size, icon_size), Image.ADAPTIVE))


        self.treeview = ttk.Treeview(self.root, show="tree")
        self.treeview.grid(row=0, column=0, sticky="nsew")
        # Call the item_opened() method each item an item
        # is expanded.
        self.treeview.tag_bind(
            "fstag", "<<TreeviewOpen>>", self.item_opened)
        # Make sure the treeview widget follows the window
        # when resizing.
        for w in (self.root, self.root):
            w.rowconfigure(0, weight=1)
            w.columnconfigure(0, weight=1)

        # This dictionary maps the treeview items IDs with the
        # path of the file or folder.
        self.fsobjects: dict[str, Path] = {}

        # Load the root directory.
        renderfarm_root = self.insert_item(os.path.join("/render", username), ".")

        self.treeview.bind("<Button-3>", self.show_filepath)

        self.load_tree(".", renderfarm_root)


    def get_icon(self, path: str) -> tk.PhotoImage:
        """
        Return a folder icon if `path` is a directory and
        a file icon otherwise.
        """

        file_extension = os.path.splitext(os.path.basename(path))[1]

        if (file_extension):
            if ("blend" in file_extension): return self.BLENDER_ICON

            if ("hip" in file_extension): return self.HOUDINI_ICON

            if (file_extension in [".ma", ".mb"]): return self.MAYA_ICON

            if (file_extension in [".png"]): return self.IMAGE_ICON

            return self.FILE_ICON
        

        elif (self.renderfarm.is_dir(path)):
            return self.FOLDER_ICON
        else:
            return self.FILE_ICON
    
    def insert_item(self, name: str, path: str = "", parent: str = "") -> str:
        """
        Insert a file or folder into the treeview and return the item ID.
        """
        iid = self.treeview.insert(
            parent, tk.END, text=name, tags=("fstag",),
            image=self.get_icon(path))
        self.fsobjects[iid] = path
        return iid
    
    def load_tree(self, path: str = "", parent: str = "") -> None:
        """
        Load the contents of `path` into the treeview.
        """
        # Check if the parent item exists in the treeview
        if parent and parent not in self.fsobjects:
            return

        for file in self.renderfarm.list_dir(path):
            full_path = os.path.join(path, file)
            child = self.insert_item(file, full_path, parent)
            # Preload the content of each directory within `path`.
            # This is necessary to make the folder item expandable.
            if self.renderfarm.is_dir(full_path):
                self.insert_item("Loading...", "", parent=child)  # Use empty string as the parent

    
    def load_subitems(self, iid: str) -> None:
        """
        Load the content of each folder inside the specified item into the treeview.
        """
        path = self.fsobjects[iid]
        if self.renderfarm.is_dir(path):
            for child in self.renderfarm.list_dir(path):
                child_path = os.path.join(path, child)
                child_iid = self.insert_item(child, child_path, parent=iid)
                # Check if the child is a directory and insert a placeholder
                if self.renderfarm.is_dir(child_path):
                    children = self.renderfarm.list_dir(child_path)
                    if len(children) > 0:
                        self.insert_item("Loading...", "", parent=child_iid)


            
    def item_opened(self, _event: tk.Event) -> None:
        """
        Handler invoked when a folder item is expanded.
        """
        # Get the expanded item
        iid = self.treeview.selection()[0]
        # Clear the selections of subitems
        for child_iid in self.treeview.get_children(iid):
            self.treeview.delete(child_iid)
        # If it is a folder, load its content
        self.load_subitems(iid)

    def show_filepath(self, event: tk.Event) -> None:
        if hasattr(self, 'context_menu'):
            self.context_menu.destroy()
            del self.context_menu
        """
        Show the file path of the selected node when right-clicked.
        """

        item = self.treeview.identify_row(event.y)
        if item in self.fsobjects:
            real_path = self.fsobjects[item]
            render_path = f"/render/{self.username}".join(self.fsobjects[item].split(".", 1))
            file_extension = os.path.splitext(os.path.basename(real_path))[1]
            # Activate the selected item
            self.treeview.selection_set(item)
            self.treeview.focus(item)
            print(real_path)

            self.context_menu = Menu(self.root, tearoff=0)
            if (render_path != f"/render/{self.username}"):
                self.context_menu.add_command(label="Delete", command=self.delete_item)

            self.context_menu.add_command(label="Download", command=self.download_item)

            if os.path.isdir(real_path):
                self.context_menu.add_command(label="Upload to", command=self.upload_to_item)
            else:
                self.context_menu.add_command(label="Open", command=self.open_item)

                if ("blend" in file_extension or "hip" in file_extension or file_extension in [".ma", ".mb"]):
                    self.context_menu.add_command(label="Render", command=self.render_item)

            self.root.bind("<Button-1>", self.hide_context_menu)

            self.context_menu.post(event.x_root, event.y_root)

    def hide_context_menu(self, _event: tk.Event) -> None:
        """
        Hide the context menu.
        """
        self.context_menu.unpost()
        self.root.bind("<Button-3>", self.show_filepath)

    def delete_item(self):
        """
        Placeholder function for deleting an item.
        """
        item = self.treeview.selection()[0]
        path = self.fsobjects[item]
        print(f"Deleting {path}")
        self.renderfarm.delete(path)

    
    def download_item(self):
        """
        Placeholder function for downloading an item.
        """
        item = self.treeview.selection()[0]
        remote_path = self.fsobjects[item]

        print("Downloading...")

        try:
            if (self.renderfarm.is_dir(remote_path)):
                local_directory = filedialog.askdirectory(title="Select Destination Folder")
                self.download_directory(remote_path, local_directory)
            else:
                file_name = os.path.basename(remote_path)
                local_path = filedialog.asksaveasfilename(title="Save file", initialfile=file_name)
                if local_path:
                    # Open the file in write mode to get the path
                    with open(local_path, "w") as file:
                        # Close the file immediately after opening
                        pass
                    self.renderfarm.download(remote_path, local_path)
            print("Download Complete")
        except Exception as err:
                print(f"Download failed: {err}")

    def download_directory(self, remote_directory, local_directory):
        """
        Recursively download a directory and its contents from the SFTP server.
        """
        # Create the local directory if it doesn't exist
        os.makedirs(local_directory, exist_ok=True)

        # List the contents of the remote directory
        remote_files = self.renderfarm.list_dir(remote_directory)

        for remote_file in remote_files:
            remote_path = os.path.join(remote_directory, remote_file)
            local_path = os.path.join(local_directory, remote_file)

            if self.renderfarm.is_dir(remote_path):
                # If the item is a directory, recursively download it
                self.download_directory(remote_path, local_path)
            else:
                # If the item is a file, download it
                self.renderfarm.download(remote_path, local_path)

    def render_item(self):
        """
        Placeholder function for rendering an item.
        """
        item = self.treeview.selection()[0]
        path = self.fsobjects[item]
        print(f"Rendering {path}")

    def upload_to_item(self):
        item = self.treeview.selection()[0]
        path = self.fsobjects[item]
        print(f"Uploading to {path}")

    def open_item(self):
        item = self.treeview.selection()[0]
        path = self.fsobjects[item]
        print(f"Opening {path}")