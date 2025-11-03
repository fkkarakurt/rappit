import gi
# Ensure the necessary GTK and Adwaita versions are loaded
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gio
import json

class ExamplesManager:
    """
    Manages a set of predefined API request examples for demonstration
    and quick testing purposes. These examples are used to populate
    the request UI fields (Method, URL, Body, Headers).
    """
    def __init__(self):
        """
        Initializes the dictionary of hardcoded API examples.
        Each key maps to a dictionary containing 'method', 'url', 'body', and 'headers'.
        """
        self.examples = {
            'jsonplaceholder_get': {
                'method': 'GET',
                'url': 'https://jsonplaceholder.typicode.com/posts/1',
                'body': '',
                'headers': {'Content-Type': 'application/json'}
            },
            'github_get': {
                'method': 'GET',
                'url': 'https://api.github.com/users/fkkarakurt',
                'body': '',
                'headers': {'Accept': 'application/vnd.github.v3+json'}
            },
            'randomuser_get': {
                'method': 'GET',
                'url': 'https://randomuser.me/api/',
                'body': '',
                'headers': {'Content-Type': 'application/json'}
            },
            'jsonplaceholder_post': {
                'method': 'POST',
                'url': 'https://jsonplaceholder.typicode.com/posts',
                'body': json.dumps({
                    "title": "Rappit Test",
                    "body": "This is a test post from Rappit",
                    "userId": 1
                }, indent=2), # Pretty-print the JSON body
                'headers': {'Content-Type': 'application/json'}
            },
            'httpbin_post': {
                'method': 'POST',
                'url': 'https://httpbin.org/post',
                'body': json.dumps({
                    "name": "Rappit",
                    "type": "API Testing Tool",
                    "version": "1.0"
                }, indent=2), # Pretty-print the JSON body
                'headers': {'Content-Type': 'application/json'}
            },
            'xml_example': {
                'method': 'GET',
                'url': 'https://httpbin.org/xml',
                'body': '',
                'headers': {'Accept': 'application/xml'}
            },
            'html_example': {
                'method': 'GET',
                'url': 'https://httpbin.org/html',
                'body': '',
                'headers': {'Accept': 'text/html'}
            }
        }

    def create_examples_menu(self):
        """
        Constructs the hierarchical GIO Menu structure for the Examples menu
        in the application's main window.

        The menu items are linked to application-level actions (e.g., 'app.example_...').

        Returns:
            Gio.Menu: The ready-to-use menu model for examples.
        """
        menu = Gio.Menu()

        # --- GET Examples Section ---
        get_section = Gio.Menu()
        get_section.append("JSONPlaceholder Posts", "app.example_jsonplaceholder_get")
        get_section.append("GitHub User", "app.example_github_get")
        get_section.append("Random User", "app.example_randomuser_get")
        get_section.append("XML Example", "app.example_xml")
        get_section.append("HTML Example", "app.example_html")
        menu.append_section("GET Examples", get_section)

        # --- POST Examples Section ---
        post_section = Gio.Menu()
        post_section.append("JSONPlaceholder Create", "app.example_jsonplaceholder_post")
        post_section.append("HTTPBin POST", "app.example_httpbin_post")
        menu.append_section("POST Examples", post_section)

        return menu

    def get_example(self, example_type):
        """
        Retrieves the data for a specific, named example.

        Args:
            example_type (str): The key corresponding to the desired example (e.g., 'jsonplaceholder_get').

        Returns:
            dict or None: The example data dictionary, or None if the key is invalid.
        """
        return self.examples.get(example_type)

    def get_example_actions(self):
        """
        Returns a list of tuples containing (action_name, example_key).
        This list is typically used by the main application to register
        the corresponding Gio.Action handlers for the menu items.

        Returns:
            list: A list of (str, str) tuples.
        """
        return [
            ('example_jsonplaceholder_get', 'jsonplaceholder_get'),
            ('example_github_get', 'github_get'),
            ('example_randomuser_get', 'randomuser_get'),
            ('example_jsonplaceholder_post', 'jsonplaceholder_post'),
            ('example_httpbin_post', 'httpbin_post'),
            ('example_xml', 'xml_example'),
            ('example_html', 'html_example')
        ]
