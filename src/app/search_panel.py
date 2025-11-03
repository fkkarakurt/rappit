import gi
# Require necessary GTK 4.0 and Adwaita 1 versions
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GObject
from typing import Optional, List, Tuple

# Define a custom GObject name for better introspection
class SearchPanel(Gtk.Box):
    """
    A persistent search panel widget used to find and highlight text within
    a target Gtk.TextView. It provides navigation controls for cycling through
    matches and dynamically highlights all occurrences.
    """
    __gtype_name__ = 'SearchPanel'

    def __init__(self, text_view: Gtk.TextView):
        """
        Initializes the panel, linking it to the target TextView.

        Args:
            text_view (Gtk.TextView): The widget where searching will take place.
        """
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.text_view = text_view
        self.buffer = text_view.get_buffer()
        self.current_match: Optional[int] = None
        self.matches: List[Tuple[Gtk.TextIter, Gtk.TextIter]] = [] # Stores (start_iter, end_iter) for all matches

        # Ensure a highlight tag exists
        self.highlight_tag = self.create_highlight_tag()

        self.setup_ui()

    def setup_ui(self):
        """
        Constructs and configures the UI elements of the search panel.
        """
        # --- Search Entry ---
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search in response...")
        self.search_entry.set_size_request(200, -1)

        # Connect signals for search initiation and navigation
        self.search_entry.connect('search-changed', self.on_search_changed)
        self.search_entry.connect('activate', self.on_next_match) # Pressing Enter goes to the next match
        self.append(self.search_entry)

        # --- Previous Match Button ---
        self.prev_btn = Gtk.Button.new_from_icon_name("go-up-symbolic")
        self.prev_btn.set_tooltip_text("Previous match")
        self.prev_btn.connect('clicked', self.on_prev_match)
        self.prev_btn.set_sensitive(False)
        self.append(self.prev_btn)

        # --- Next Match Button ---
        self.next_btn = Gtk.Button.new_from_icon_name("go-down-symbolic")
        self.next_btn.set_tooltip_text("Next match")
        self.next_btn.connect('clicked', self.on_next_match)
        self.next_btn.set_sensitive(False)
        self.append(self.next_btn)

        # --- Close Button ---
        close_btn = Gtk.Button.new_from_icon_name("window-close-symbolic")
        close_btn.set_tooltip_text("Close search")
        close_btn.connect('clicked', self.on_close_search)
        self.append(close_btn)

    # --- Tag Management ---

    def create_highlight_tag(self) -> Gtk.TextTag:
        """
        Creates and configures the Gtk.TextTag used for highlighting search matches.
        """
        # Use a consistent tag name to ensure we only create one tag
        tag = self.buffer.create_tag("search_highlight")
        tag.set_property("background", "#ffff00") # Bright yellow background
        tag.set_property("foreground", "black")
        return tag

    def clear_highlights(self):
        """
        Removes all search highlight tags from the buffer and resets internal match tracking.
        """
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        # Remove the specific highlight tag from the entire buffer
        self.buffer.remove_tag_by_name("search_highlight", start_iter, end_iter)

        # Also clear any current text selection
        self.buffer.select_range(start_iter, start_iter)

        self.matches = []
        self.current_match = None
        self.update_buttons() # Update counts and sensitivity

    # --- Search Logic ---

    def on_search_changed(self, entry):
        """
        Handles search text changes: clears old highlights, finds all new matches,
        and jumps to the first match.
        """
        search_text = entry.get_text().strip()
        self.clear_highlights()

        if search_text:
            self.highlight_all_matches(search_text)
            if self.matches:
                # Jump to the first match and select it
                self.current_match = 0
                match_start, match_end = self.matches[self.current_match]
                self.select_match(match_start, match_end)

            self.update_buttons()
        else:
            self.update_buttons() # Reset buttons when the entry is empty

    def highlight_all_matches(self, search_text: str):
        """
        Iterates through the entire TextBuffer, finds all occurrences of the search text,
        applies the highlight tag, and stores the match iterators.
        """
        start_iter = self.buffer.get_start_iter()

        # Store matches to enable quick navigation
        self.matches = []

        while True:
            # Case-insensitive search
            match = start_iter.forward_search(
                search_text,
                Gtk.TextSearchFlags.CASE_INSENSITIVE,
                None
            )

            if not match:
                break

            match_start, match_end = match
            self.matches.append((match_start.copy(), match_end.copy())) # Store copies of iterators

            # Apply the persistent highlight tag
            self.buffer.apply_tag(self.highlight_tag, match_start, match_end)

            # Continue search from the end of the last match to avoid infinite loops
            start_iter = match_end

    # --- Navigation ---

    def on_next_match(self, widget=None):
        """Cycles to and displays the next search match."""
        if not self.matches or self.current_match is None:
            return

        # Circular navigation: advance index and wrap around
        self.current_match = (self.current_match + 1) % len(self.matches)

        match_start, match_end = self.matches[self.current_match]
        self.select_match(match_start, match_end)
        self.update_buttons()

    def on_prev_match(self, widget):
        """Cycles to and displays the previous search match."""
        if not self.matches or self.current_match is None:
            return

        # Circular navigation: decrease index and wrap around
        self.current_match = (self.current_match - 1) % len(self.matches)

        match_start, match_end = self.matches[self.current_match]
        self.select_match(match_start, match_end)
        self.update_buttons()

    def select_match(self, start_iter: Gtk.TextIter, end_iter: Gtk.TextIter):
        """
        Selects the given match range in the buffer and scrolls the TextView
        to make the selection visible.
        """
        # Select the text range
        self.buffer.select_range(start_iter, end_iter)

        # Scroll the text view to bring the start of the match into view
        self.text_view.scroll_to_iter(start_iter, 0.1, False, 0, 0)

    def update_buttons(self):
        """
        Updates the sensitivity of the navigation buttons and sets the match count
        in the search entry's placeholder text.
        """
        has_matches = bool(self.matches)
        self.prev_btn.set_sensitive(has_matches)
        self.next_btn.set_sensitive(has_matches)

        if has_matches and self.current_match is not None:
            # Display current match index / total matches (e.g., 5/12)
            count_text = f"{self.current_match + 1}/{len(self.matches)}"
            self.search_entry.set_placeholder_text(f"Search... ({count_text})")
        else:
             self.search_entry.set_placeholder_text("Search in response...")

    def on_close_search(self, widget):
        """
        Handler for the 'Close' button. Clears all highlights and hides the panel.
        """
        self.clear_highlights()
        self.search_entry.set_text("")
        self.set_visible(False)
