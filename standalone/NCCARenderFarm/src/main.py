"""
    Simple File System Explorer with Tk
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from PIL import Image, ImageTk


from utils import *

class NCCARenderFarmApplication():
    
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.os = get_os_type()

        self.root.geometry("700x500")

        if (os == "other"):
            raise Exception("Current operating system not supported.")

        self.user= get_user_name()

        self.renderfarm = get_renderfarm()
        self.application_folder = os.path.dirname(os.path.dirname(__file__))

        # configure icons

        BROWSER_ICON_SIZE = (16, 16)

        self.FILE_ICON = ImageTk.PhotoImage(Image.open(os.path.join(self.application_folder, "assets/icons/text-x-generic.png")).resize(BROWSER_ICON_SIZE, Image.ADAPTIVE))
        self.FOLDER_ICON = ImageTk.PhotoImage(Image.open(os.path.join(self.application_folder, "assets/icons/folder.png")).resize(BROWSER_ICON_SIZE, Image.ADAPTIVE))

        self.IMAGE_ICON = ImageTk.PhotoImage(Image.open(os.path.join(self.application_folder, "assets/icons/image-x-generic.png")).resize(BROWSER_ICON_SIZE, Image.ADAPTIVE))
        self.HOUDINI_ICON = ImageTk.PhotoImage(Image.open(os.path.join(self.application_folder, "assets/icons/houdini.png")).resize(BROWSER_ICON_SIZE, Image.ADAPTIVE))
        self.MAYA_ICON = ImageTk.PhotoImage(Image.open(os.path.join(self.application_folder, "assets/icons/maya.png")).resize(BROWSER_ICON_SIZE, Image.ADAPTIVE))
        self.BLENDER_ICON = ImageTk.PhotoImage(Image.open(os.path.join(self.application_folder, "assets/icons/blender.png")).resize(BROWSER_ICON_SIZE, Image.ADAPTIVE))


        self.root.title("NCCA Render Farm")
        # show="tree" removes the column header, since we
        # are not using the table feature.


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
        renderfarm_root = self.insert_item(os.path.join("/render", self.user), ".")

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
        """
        Show the file path of the selected node when right-clicked.
        """

        item = self.treeview.identify_row(event.y)
        if item in self.fsobjects:
            path = f"/render/{self.user}".join(self.fsobjects[item].split(".", 1))
            # Activate the selected item
            self.treeview.selection_set(item)
            self.treeview.focus(item)

            print(path)

    def start(self):
        self.root.mainloop()

def main():
    app = NCCARenderFarmApplication()
    app.start()

if __name__ == "__main__":
    main()