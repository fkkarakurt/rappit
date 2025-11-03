import sys
import gi

# Require necessary GTK, Adwaita, and GIO versions
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gio', '2.0')

from gi.repository import Gtk, Adw, Gio, Gdk
# Import the main application window (assuming it's in the same module path)
from .window import MainWindow

class RappitApplication(Adw.Application):
    """
    The main application class for Rappit, inheriting from Adw.Application.
    It manages the application lifecycle, global actions, and window instantiation.
    """
    def __init__(self):
        """
        Initializes the Adwaita Application with a unique ID and default flags.
        """
        super().__init__(application_id='io.github.fkkarakurt.rappit',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        # Set up all global application actions (menu items, shortcuts)
        self.create_actions()

    def do_activate(self):
        """
        Called when the application is launched or activated (e.g., from the dock).
        It ensures a main window is active and visible.
        """
        # Check if a window is already active
        win = self.props.active_window
        if not win:
            # If no window is open, create and show a new MainWindow instance
            win = MainWindow(application=self)

        # Bring the window to the foreground and display it
        win.present()

    def create_actions(self):
        """
        Defines and registers all application-level Gio.SimpleAction objects
        and sets their keyboard accelerators (shortcuts).
        """
        # Basic application-level actions (Quit, About, Preferences, etc.)
        actions = [
            # (name, callback_method, shortcuts_list)
            ('quit', self.on_quit, ['<primary>q']),
            ('about', self.on_about, []),
            ('preferences', self.on_preferences, ['<primary>comma']),
            ('new_request', self.on_new_request, ['<primary>n']),
            ('send_request', self.on_send_request, ['<primary>Return']), # Primary=Ctrl on Linux/Windows, Command on macOS
            ('find_in_response', self.on_find, ['<primary>f']),
            ('export_response', self.on_export, ['<primary>e']),
        ]

        # Example actions: These actions are defined at the application level
        # but their 'activate' signal will be handled by the MainWindow (the active window)
        example_actions = [
            'example_jsonplaceholder_get',
            'example_github_get',
            'example_randomuser_get',
            'example_jsonplaceholder_post',
            'example_httpbin_post',
            'example_xml',
            'example_html'
        ]

        # 1. Register Example actions (no explicit callback here, handled by the window)
        for action_name in example_actions:
            action = Gio.SimpleAction.new(action_name, None)
            self.add_action(action)

        # 2. Register primary actions with their callbacks and shortcuts
        for name, callback, shortcuts in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect('activate', callback)
            self.add_action(action)

            # Apply keyboard shortcuts
            if shortcuts:
                self.set_accels_for_action(f'app.{name}', shortcuts)

    # --- Action Handler Methods ---

    def on_quit(self, action, param):
        """Handler for the 'quit' action. Terminates the application."""
        self.quit()

    def on_about(self, action, param):
        """Handler for the 'about' action. Displays the Adwaita About Window."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name='Rappit',
            application_icon='io.github.fkkarakurt.rappit',
            developer_name='Fatih Küçükkarakurt',
            version='1.0.0',
            developers=['Fatih Küçükkarakurt'],
            copyright='© 2025 Fatih Küçükkarakurt',
            license_type=Gtk.License.GPL_3_0,
            website='https://github.com/fkkarakurt/rappit',
            issue_url='https://github.com/fkkarakurt/rappit/issues',
            comments='Fast and lightweight API testing tool',
        )
        about.add_credit_section("Contributors", ["Fatih Küçükkarakurt"])
        about.present()

    def on_preferences(self, action, param):
        """Handler for the 'preferences' action. Placeholder for future settings window."""
        print("Preferences opened") # TODO: Implement preferences dialog

    def on_new_request(self, action, param):
        """Handler for the 'new_request' action. Delegates the operation to the active window."""
        win = self.props.active_window
        if win and hasattr(win, 'on_new_request'):
            win.on_new_request()

    def on_send_request(self, action, param):
        """Handler for the 'send_request' action. Triggers the request sending process in the active window."""
        win = self.props.active_window
        if win and hasattr(win, 'on_send_clicked'):
            win.on_send_clicked()

    def on_find(self, action, param):
        """Handler for the 'find_in_response' action. Activates the search bar in the response view."""
        win = self.props.active_window
        if win and hasattr(win, 'on_search_response'):
            win.on_search_response()

    def on_export(self, action, param):
        """Handler for the 'export_response' action. Initiates the response data export process."""
        win = self.props.active_window
        if win and hasattr(win, 'on_export'):
            win.on_export()

# --- Application Startup ---

def main():
    """
    Main entry point function to instantiate and run the application.
    """
    app = RappitApplication()
    return app.run(sys.argv)
