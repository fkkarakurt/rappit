import gi
# Require GTK 4.0 and Adwaita 1 for the modern GNOME/GTK look and feel
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

class HeadersPanel(Adw.PreferencesGroup):
    """
    A custom preferences group widget designed to manage and display
    HTTP request headers. Users can add, edit, and remove custom headers.
    It inherits from Adw.PreferencesGroup for a native-looking GNOME settings panel style.
    """
    def __init__(self):
        # Initialize the parent class with a title and a descriptive summary
        super().__init__(title="Request Headers", description="Custom HTTP headers for your request")

        # Internal dictionary to hold the current header key-value pairs (Note: Currently populated from UI on get_headers)
        self.headers = {}

        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the visual layout of the panel, including the header list container
        and the 'Add Header' button.
        """
        # Headers list container: A vertical box to hold individual header rows
        self.headers_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.headers_list.set_margin_top(12)
        self.headers_list.set_margin_bottom(12)

        self.add(self.headers_list)

        # Populate the panel with a set of default, commonly used headers
        self.add_default_headers()

        # Add button for creating a new, empty header row
        add_btn = Gtk.Button.new_with_label("Add Header")
        add_btn.set_margin_top(6)
        # Connect the button click signal to the handler method
        add_btn.connect('clicked', self.on_add_header)
        self.add(add_btn)

    def add_default_headers(self):
        """
        Initializes the panel with some common default HTTP headers.
        """
        default_headers = [
            ("Content-Type", "application/json"),
            ("User-Agent", "Rappit/1.0"),
            ("Accept", "*/*")
        ]

        for key, value in default_headers:
            self.add_header_row(key, value)

    def add_header_row(self, key="", value=""):
        """
        Creates and appends a new row widget containing Key, Value entry fields,
        and a Delete button to the headers list.

        Args:
            key (str): Initial text for the header key entry.
            value (str): Initial text for the header value entry.
        """
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.set_margin_top(3)
        row.set_margin_bottom(3)

        # Key entry field
        key_entry = Gtk.Entry()
        key_entry.set_placeholder_text("Header Name")
        key_entry.set_text(key)
        key_entry.set_hexpand(True) # Ensure the key entry expands horizontally

        # Value entry field
        value_entry = Gtk.Entry()
        value_entry.set_placeholder_text("Header Value")
        value_entry.set_text(value)
        value_entry.set_hexpand(True) # Ensure the value entry expands horizontally

        # Delete button
        delete_btn = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        delete_btn.add_css_class('destructive-action') # Apply a destructive style for visual emphasis
        delete_btn.set_tooltip_text("Remove header")
        # Pass the current row as user data to the delete handler
        delete_btn.connect('clicked', self.on_delete_header, row)

        row.append(key_entry)
        row.append(value_entry)
        row.append(delete_btn)

        self.headers_list.append(row)

    def on_add_header(self, button):
        """Handler for the 'Add Header' button click."""
        self.add_header_row()

    def on_delete_header(self, button, row):
        """Handler for the 'Delete' button click, removes the corresponding row from the UI."""
        self.headers_list.remove(row)

    def get_headers(self):
        """
        Parses the current state of the UI and returns the headers as a Python dictionary.
        Only rows with both a non-empty key and value are included.

        Returns:
            dict: A dictionary of {header_key: header_value}.
        """
        headers = {}

        child = self.headers_list.get_first_child()
        while child is not None:
            if isinstance(child, Gtk.Box):
                # Retrieve the entries within the Gtk.Box row
                key_entry = child.get_first_child()
                value_entry = key_entry.get_next_sibling() if key_entry else None

                if key_entry and value_entry:
                    # Retrieve and clean up the text values
                    key = key_entry.get_text().strip()
                    value = value_entry.get_text().strip()

                    # Only include non-empty, valid headers
                    if key and value:
                        headers[key] = value

            child = child.get_next_sibling()

        return headers
