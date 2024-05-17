"""
    Simple File System Explorer with Tk
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from utils import *

class NCCARenderFarmApplication(ttk.Frame):
    
    def __init__(self, window: tk.Tk | tk.Toplevel) -> None:
        super().__init__(window)
        self.os = get_os_type()

        if (os == "other"):
            raise Exception("Current operating system not supported.")

        self.user= get_user_name()

        self.renderfarm = get_renderfarm()


        self.application_folder = os.path.dirname(os.path.dirname(__file__))

        window.title("NCCA Render Farm")
        # show="tree" removes the column header, since we
        # are not using the table feature.
        self.treeview = ttk.Treeview(self, show="tree")
        self.treeview.grid(row=0, column=0, sticky="nsew")
        # Call the item_opened() method each item an item
        # is expanded.
        self.treeview.tag_bind(
            "fstag", "<<TreeviewOpen>>", self.item_opened)
        # Make sure the treeview widget follows the window
        # when resizing.
        for w in (self, window):
            w.rowconfigure(0, weight=1)
            w.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")
        # This dictionary maps the treeview items IDs with the
        # path of the file or folder.
        self.fsobjects: dict[str, Path] = {}
        self.file_image = tk.PhotoImage(file=os.path.join(self.application_folder, "assets/icons/file.png"))
        self.folder_image = tk.PhotoImage(file=os.path.join(self.application_folder, "assets/icons/folder.png"))
        # Load the root directory.
        self.load_tree(".")
    
    def get_icon(self, path: Path) -> tk.PhotoImage:
        """
        Return a folder icon if `path` is a directory and
        a file icon otherwise.
        """
        return self.folder_image if self.renderfarm.isdir(path) else self.file_image
    
    def insert_item(self, name: str, path: Path, parent: str = "") -> str:
        """
        Insert a file or folder into the treeview and return the item ID.
        """
        iid = self.treeview.insert(
            parent, tk.END, text=name, tags=("fstag",),
            image=self.get_icon(path))
        self.fsobjects[iid] = path
        return iid
    
    def get_icon(self, path: Path) -> tk.PhotoImage:
        """
        Return a folder icon if `path` is a directory and a file icon otherwise.
        """
        return self.folder_image if os.path.isdir(path) else self.file_image
    
    def insert_item(self, name: str, path: Path, parent: str = "") -> str:
        """
        Insert a file or folder into the treeview and return the item ID.
        """
        iid = self.treeview.insert(
            parent, tk.END, text=name, tags=("fstag",),
            image=self.get_icon(path))
        self.fsobjects[iid] = path
        return iid
    
    def load_tree(self, path: Path, parent: str = "") -> None:
        """
        Load the contents of `path` into the treeview. 
        """
        for obj in self.renderfarm.listdir(path):
            fullpath = os.path.join(path,obj)
            child = self.insert_item(obj, fullpath, parent)
            # Preload the content of each directory within `path`.
            # This is necessary to make the folder item expandable.
            if os.path.isdir(fullpath):
                self.insert_item("Loading...", fullpath, child)
    
    def load_subitems(self, iid: str) -> None:
        """
        Load the content of each folder inside the specified item into the treeview.
        """
        for child_iid in self.treeview.get_children(iid):
            if self.fsobjects[child_iid].is_dir():
                self.load_tree(self.fsobjects[child_iid], parent=child_iid)
    
    def item_opened(self, _event: tk.Event) -> None:
        """
        Handler invoked when a folder item is expanded.
        """
        # Get the expanded item
        iid = self.treeview.selection()[0]
        # If it is a folder, load its content
        self.load_subitems(iid)

def main():
    root = tk.Tk()
    app = NCCARenderFarmApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()