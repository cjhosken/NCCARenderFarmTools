import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

class FolderTreeView(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Folder Treeview")
        self.set_default_size(800, 600)

        # Create a Paned container
        self.paned = Gtk.Paned()
        self.add(self.paned)

        # Create the side panel
        self.side_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.paned.pack1(self.side_panel, resize=False, shrink=False)

        # Create buttons
        button_labels = ["Button 1", "Button 2", "Button 3", "Button 4", "Button 5", "Button 6"]
        for label in button_labels:
            button = Gtk.Button(label=label)
            button.set_size_request(100, 100)  # Set button size
            button.connect("clicked", self.on_button_clicked)
            self.side_panel.pack_start(button, False, False, 0)

        # Create a TreeStore model
        self.tree_store = Gtk.TreeStore(str, str, str)

        # Create a TreeView
        self.tree_view = Gtk.TreeView(model=self.tree_store)
        self.tree_view.set_headers_visible(False)

        # Add an icon column to the TreeView
        renderer_pixbuf = Gtk.CellRendererPixbuf()
        column_pixbuf = Gtk.TreeViewColumn("", renderer_pixbuf, icon_name=2)
        self.tree_view.append_column(column_pixbuf)

        # Add a text column to the TreeView
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Name", renderer_text, text=0)
        self.tree_view.append_column(column_text)

        # Set up selection handling
        selection = self.tree_view.get_selection()
        selection.connect("changed", self.on_selection_changed)

        # Set up expansion handling
        self.tree_view.connect("row-expanded", self.on_row_expanded)
        self.tree_view.connect("row-collapsed", self.on_row_collapsed)

        # Create a ScrolledWindow to contain the TreeView
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.add(self.tree_view)

        # Add the ScrolledWindow to the center panel
        self.paned.pack2(scrolled_window, resize=True, shrink=True)

        # Add the ScrolledWindow to the window
        self.add(self.paned)

        # Set initial directory
        initial_directory = "/home/cjhosken"
        self.populate_tree_store(self.tree_store, initial_directory)

        # Expand the root folder
        root_iter = self.tree_store.get_iter_first()
        self.tree_view.expand_row(self.tree_store.get_path(root_iter), True)

    def populate_tree_store(self, tree_store, directory, parent=None):
        if parent is None:
            parent_iter = tree_store.append(None, ["PROJECT", directory, "folder"])
            # Set the first root folder as non-closable
            tree_store.set_value(parent_iter, 2, "non-closable")
        else:
            parent_iter = tree_store.append(parent, [os.path.basename(directory), directory, "folder"])

        # Dynamically load folder items when expanded
        tree_store.append(parent_iter, ["Loading...", "loading", "loading"])

    def on_selection_changed(self, selection):
        model, iter = selection.get_selected()
        if iter:
            print("Selected:", model[iter][0])

    def on_row_expanded(self, treeview, iter, path):
        model = treeview.get_model()
        if model.iter_has_child(iter):
            child_iter = model.iter_children(iter)
            if model.get_value(child_iter, 2) == "loading":
                # Load folder items
                directory = model.get_value(iter, 1)
                model.remove(child_iter)
                self.populate_children(model, directory, iter)

    def populate_children(self, tree_store, directory, parent):
        parent_iter = None
        try:
            for item in sorted(os.listdir(directory)):
                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    child_iter = tree_store.append(parent, [item, full_path, "folder"])
                    if os.listdir(full_path):
                        tree_store.append(child_iter, ["Loading...", "loading", "loading"])
                else:
                    file_info = Gio.File.new_for_path(full_path).query_info('standard::icon', Gio.FileQueryInfoFlags.NONE, None)
                    icon = file_info.get_icon()
                    icon_name = icon.get_names()[0] if icon else "gtk-file"
                    tree_store.append(parent, [item, full_path, icon_name])
        except PermissionError:
            print("Permission denied:", directory)

    def on_row_collapsed(self, treeview, iter, path):
        pass

    def on_button_clicked(self, button):
        print(f"{button.get_label()} clicked")

win = FolderTreeView()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()