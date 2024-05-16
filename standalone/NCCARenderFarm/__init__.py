import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class NCCA_RenderFarmApplication():

    def __init__(self) -> None:
        self.window = Gtk.Window()
        self.window.set_title("NCCA Render Farm")
        self.window.set_size_request(720, 250)
        self.window.connect("delete-event", Gtk.main_quit)

        self.file_dialog = Gtk.FileChooserDialog("Please choose a file", None,
                                         Gtk.FileChooserAction.OPEN,
                                         (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                          Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        
        button = Gtk.Button(label="Select File")
        button.connect("clicked", self.button_clicked)

        self.window.add(button)


    def button_clicked(self, widget):
        file_dialog = Gtk.FileChooserDialog("Please choose a file", None,
                                            Gtk.FileChooserAction.OPEN,
                                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        file_dialog.set_default_size(800, 400)

        response = file_dialog.run()
        if response == Gtk.ResponseType.OK:
            print("File selected: ", file_dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("File selection cancelled")

        file_dialog.destroy()


    def run(self):
        self.window.show_all()
        Gtk.main()




def main():
    app = NCCA_RenderFarmApplication()
    app.run()

if __name__ == "__main__":
    main()