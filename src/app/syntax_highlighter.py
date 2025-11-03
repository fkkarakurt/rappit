import gi
# Require core GTK and GtkSource (the syntax highlighting component)
gi.require_version('Gtk', '4.0')
gi.require_version('GtkSource', '5')

from gi.repository import Gtk, GtkSource
import json
from typing import Optional

class SyntaxHighlighter:
    """
    Manages the creation and configuration of GtkSource.View widgets,
    including setting syntax highlighting, style schemes, and code-editing features.
    It also provides logic for intelligently detecting the content type.
    """
    def __init__(self):
        """
        Initializes the necessary GtkSource managers.
        """
        # Manager for available programming languages (e.g., Python, JSON, XML)
        self.language_manager = GtkSource.LanguageManager()
        # Manager for color themes (e.g., 'classic', 'dark', 'oblivion')
        self.style_manager = GtkSource.StyleSchemeManager()

    def set_buffer(self, buffer):
        """
        Set the buffer for syntax highlighting - this might be what was intended.
        """
        if hasattr(buffer, 'set_language'):
            lang = self.language_manager.get_language('text')
            if lang:
                buffer.set_language(lang)
        print("✅ Buffer set for syntax highlighting")

    def create_source_view(self, language: Optional[str] = None) -> GtkSource.View:
        """
        Creates a pre-configured GtkSource.View for displaying code or content
        with syntax highlighting and standard editing features enabled.

        Args:
            language (str, optional): The GtkSource language ID (e.g., 'json', 'xml') to apply.

        Returns:
            GtkSource.View: The configured text view widget.
        """
        buffer = GtkSource.Buffer()
        view = GtkSource.View(buffer=buffer)

        # --- 1. Apply Style Scheme (Color Theme) ---
        # Set a common, dark/light compatible scheme, e.g., 'classic'
        style_scheme = self.style_manager.get_scheme('classic')
        if style_scheme:
            buffer.set_style_scheme(style_scheme)

        # --- 2. Apply Syntax Language ---
        if language:
            lang = self.language_manager.get_language(language)
            if lang:
                buffer.set_language(lang)

        # --- 3. Configure Editor Properties ---
        view.set_monospace(True)
        view.set_editable(True)
        view.set_wrap_mode(Gtk.WrapMode.WORD)
        view.set_show_line_numbers(True)
        view.set_highlight_current_line(True)
        view.set_auto_indent(True)

        return view

    def set_content(self, source_view: GtkSource.View, content: str, content_type: Optional[str] = None):
        """
        Sets the content of the SourceView and applies the appropriate language highlighting.
        """
        # Detect the language based on content type and/or content structure
        language_id = self.detect_language(content, content_type)

        # Apply the language to the buffer
        lang = self.language_manager.get_language(language_id)
        if lang:
            source_view.get_buffer().set_language(lang)

        # Set the text content
        source_view.get_buffer().set_text(content)

    def detect_language(self, content: str, content_type: Optional[str] = None) -> str:
        """
        Analyzes the content and optional Content-Type header to determine the
        most suitable GtkSource language ID for syntax highlighting.

        Args:
            content (str): The raw text content (e.g., API response body).
            content_type (str, optional): The MIME type from the HTTP response header.

        Returns:
            str: The determined language ID (e.g., 'json', 'xml', 'html', or 'text').
        """
        if not content:
            return 'text'

        content = content.strip()

        # --- 1. Detection by Content-Type Header (Highest Priority) ---
        if content_type:
            mime_type = content_type.lower()
            if 'json' in mime_type:
                return 'json'
            elif 'xml' in mime_type:
                return 'xml'
            elif 'html' in mime_type:
                return 'html'

        # --- 2. Detection by Content Structure (Heuristics) ---

        # Check for JSON structure
        if content.startswith('{') or content.startswith('['):
            try:
                # Full parsing check is more reliable than just checking first character
                json.loads(content)
                return 'json'
            except:
                # If it looks like JSON but is invalid, continue to other checks
                pass

        # Check for XML/HTML structure
        if content.startswith('<?xml') or content.startswith('<'):
            if '<html' in content.lower():
                return 'html'
            else:
                return 'xml'

        # --- 3. Default Fallback ---
        return 'text'
