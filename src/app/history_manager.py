import gi
# Ensure the necessary GTK 4.0 version is loaded
gi.require_version('Gtk', '4.0')
# Adw is not strictly needed here but often accompanies GTK 4.0 in modern apps.
# Since it's not directly used, we can omit the Adw require_version and import for cleaner code.
# gi.require_version('Adw', '1')

from gi.repository import Gtk

class HistoryManager:
    """
    Manages the history of API requests within the application.
    It links request/response data with corresponding Gtk.ListBoxRow elements
    and enforces a maximum history size.
    """
    def __init__(self, history_list: Gtk.ListBox):
        """
        Initializes the manager.

        Args:
            history_list (Gtk.ListBox): The GTK widget where history items will be displayed.
        """
        self.history_list = history_list
        # Stores the detailed data for each request, indexed by a unique key.
        self.history_data = {}
        self.max_items = 20 # Maximum number of history items to keep.

    # --- Public API Methods ---

    def add_to_history(self, method: str, url: str, response: dict, request_body: str, headers: dict):
        """
        Adds a new request/response entry to the history or updates an existing one.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            url (str): The requested URL.
            response (dict): The complete response data (including status_code, response_time, etc.).
            request_body (str): The raw body sent with the request.
            headers (dict): The headers sent with the request.
        """
        if not url:
            return

        # Create a unique key to identify the request (Method + URL)
        request_key = f"{method}_{url}"

        if request_key in self.history_data:
            self._update_history_item(request_key, response)
        else:
            self._create_history_item(request_key, method, url, response, request_body, headers)

    def clear_history(self):
        """
        Removes all items from both the internal data model and the Gtk.ListBox UI.
        """
        for request_key in list(self.history_data.keys()):
            self.remove_history_item(request_key)

    def get_history_data(self, request_key: str):
        """Retrieves the detailed data for a specific history item."""
        return self.history_data.get(request_key)

    def connect_history_activated(self, callback):
        """Connects a callback function to the 'row-activated' signal of the Gtk.ListBox."""
        self.history_list.connect('row-activated', callback)

    def get_request_key_from_row(self, row: Gtk.ListBoxRow):
        """
        Retrieves the unique request key associated with a given Gtk.ListBoxRow widget.

        Args:
            row (Gtk.ListBoxRow): The activated row widget.

        Returns:
            str or None: The corresponding request key or None if not found.
        """
        for request_key, data in self.history_data.items():
            if data.get('row') == row:
                return request_key
        return None

    # --- Private Utility Methods ---

    def _create_history_item(self, request_key: str, method: str, url: str, response: dict, request_body: str, headers: dict):
        """
        Constructs the UI elements and saves the request data for a new history entry.
        """

        # Determine status emoji based on HTTP status code range
        status_code = response.get('status_code', 0)
        if 200 <= status_code < 300:
            status_emoji = "✅" # Success
        elif 300 <= status_code < 400:
            status_emoji = "⚠️" # Redirection
        else:
            status_emoji = "❌" # Client/Server Error

        # Main container for the row content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        main_box.set_margin_top(6)
        main_box.set_margin_bottom(6)

        # Title Label: Displays the Method and URL
        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{method} {url}</b>")
        title_label.set_xalign(0) # Align left
        title_label.set_wrap(True)
        title_label.set_wrap_mode(Gtk.WrapMode.WORD)
        main_box.append(title_label)

        # Subtitle Label: Displays Status and Response Time
        subtitle_label = Gtk.Label()
        subtitle_label.set_markup(f"<small>{status_emoji} Status: {status_code} | Time: {response.get('response_time', 0)}ms</small>")
        subtitle_label.set_xalign(0) # Align left
        subtitle_label.add_css_class('dim-label') # Use a dimmed text style
        main_box.append(subtitle_label)

        # Create the ListBoxRow and embed the content box
        row = Gtk.ListBoxRow()
        row.set_child(main_box)
        row.set_activatable(True)

        # Insert the new row at the beginning (index 0) to show the most recent first
        self.history_list.insert(row, 0)

        # Store the data and UI references for future lookups/updates
        self.history_data[request_key] = {
            'method': method,
            'url': url,
            'response': response,
            'body': request_body,
            'headers': headers,
            'row': row,
            'title_label': title_label,
            'subtitle_label': subtitle_label # Store reference for direct update
        }

        # Enforce maximum item limit
        if len(self.history_data) > self.max_items:
            self._remove_oldest_item()

    def _update_history_item(self, request_key: str, response: dict):
        """
        Updates the response data and refreshes the UI labels for an existing history item.
        The row is moved to the top of the list upon update.
        """
        if request_key not in self.history_data:
            return

        data = self.history_data[request_key]
        data['response'] = response

        # Determine new status emoji
        status_code = response.get('status_code', 0)
        if 200 <= status_code < 300:
            status_emoji = "✅"
        elif 300 <= status_code < 400:
            status_emoji = "⚠️"
        else:
            status_emoji = "❌"

        # Update the Subtitle Label with the new status and time
        if 'subtitle_label' in data:
            data['subtitle_label'].set_markup(f"<small>{status_emoji} Status: {status_code} | Time: {response.get('response_time', 0)}ms</small>")

        # Move the updated row to the top of the list
        if 'row' in data:
            self.history_list.remove(data['row'])
            self.history_list.insert(data['row'], 0)

    def _remove_oldest_item(self):
        """
        Removes the oldest (first created) item when the maximum capacity is exceeded.
        """
        if not self.history_data:
            return

        # Get the key of the oldest item (list(keys) maintains insertion order in modern Python)
        oldest_key = list(self.history_data.keys())[0]
        self.remove_history_item(oldest_key)

    def remove_history_item(self, request_key: str):
        """
        Removes a specific item from the data model and the UI.
        """
        if request_key in self.history_data:
            data = self.history_data[request_key]
            if 'row' in data:
                self.history_list.remove(data['row'])
            del self.history_data[request_key]
