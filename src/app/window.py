import os
import gi
from typing import Dict, Any, Optional

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GtkSource', '5')

from gi.repository import Gtk, Adw, Gio, GLib
from .headers_panel import HeadersPanel
from .request_handler import RequestHandler
from .syntax_highlighter import SyntaxHighlighter
from .search_panel import SearchPanel
from .formatter import Formatter
from .history_manager import HistoryManager
from .examples_manager import ExamplesManager
from .settings_manager import SettingsManager
from .preferences_window import PreferencesWindow

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(1200, 800)
        self.set_title("Rappit - API Testing Tool")

        # Core Components
        self.request_handler = RequestHandler()
        self.syntax_highlighter = SyntaxHighlighter()
        self.formatter = Formatter()
        self.examples_manager = ExamplesManager()
        self.settings_manager = SettingsManager()

        # UI State
        self.search_panel = None
        self.preferences_window = None
        self.last_content_type = ""

        # Build UI
        self.setup_ui()
        self.setup_actions()

        # History Manager (requires history_list from setup_ui)
        self.history_manager = HistoryManager(self.history_list)
        self.history_manager.connect_history_activated(self.on_history_activated)

        # Apply settings after UI is ready
        GLib.idle_add(self.apply_initial_settings)

    def setup_ui(self):
        """Constructs the main user interface layout"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        # Header Bar
        self.setup_header_bar(main_box)

        # Main Content Area
        content_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        content_paned.set_position(300)
        main_box.append(content_paned)

        # Sidebar (History)
        self.setup_sidebar(content_paned)

        # Main Content (Request/Response)
        self.setup_main_content(content_paned)

    def setup_header_bar(self, parent):
        """Setup header bar with actions"""
        self.header_bar = Adw.HeaderBar()
        parent.append(self.header_bar)

        # Left side buttons
        new_btn = Gtk.Button.new_with_label("New")
        new_btn.set_tooltip_text("New Request (Ctrl+N)")
        new_btn.connect('clicked', self.on_new_request)
        self.header_bar.pack_start(new_btn)

        examples_btn = Gtk.MenuButton()
        examples_btn.set_label("Examples")
        examples_btn.set_tooltip_text("API Examples")
        examples_btn.set_menu_model(self.examples_manager.create_examples_menu())
        self.header_bar.pack_start(examples_btn)

        preferences_btn = Gtk.Button.new_from_icon_name("preferences-system-symbolic")
        preferences_btn.set_tooltip_text("Preferences")
        preferences_btn.connect('clicked', self.on_preferences)
        self.header_bar.pack_start(preferences_btn)

        # Right side buttons
        self.send_btn = Gtk.Button.new_with_label("Send")
        self.send_btn.add_css_class('suggested-action')
        self.send_btn.set_tooltip_text("Send Request (Ctrl+Enter)")
        self.send_btn.connect('clicked', self.on_send_clicked)
        self.header_bar.pack_end(self.send_btn)

    def setup_sidebar(self, parent):
        """Setup left sidebar with history"""
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sidebar.set_size_request(280, -1)

        # History section
        history_group = Adw.PreferencesGroup(title="History", description="Recent requests with responses")

        self.history_list = Gtk.ListBox()
        self.history_list.add_css_class('rich-list')
        self.history_list.set_selection_mode(Gtk.SelectionMode.SINGLE)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.history_list)
        scrolled.set_vexpand(True)
        history_group.add(scrolled)

        clear_btn = Gtk.Button.new_with_label("Clear History")
        clear_btn.connect('clicked', self.on_clear_history)
        clear_btn.set_margin_top(6)
        history_group.add(clear_btn)

        sidebar.append(history_group)
        parent.set_start_child(sidebar)

    def setup_main_content(self, parent):
        """Setup main content area with URL bar, headers, request/response panels"""
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # URL Bar
        self.setup_url_bar(content_box)

        # Headers Section
        self.setup_headers_section(content_box)

        # Request/Response Split
        main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        main_paned.set_position(600)

        # Request Panel
        request_panel = self.setup_request_panel()
        main_paned.set_start_child(request_panel)

        # Response Panel
        response_panel = self.setup_response_panel()
        main_paned.set_end_child(response_panel)

        content_box.append(main_paned)
        parent.set_end_child(content_box)

    def setup_url_bar(self, parent):
        """Setup URL and method input"""
        url_group = Adw.PreferencesGroup(title="Request URL")

        url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Method dropdown
        self.method_combo = Gtk.ComboBoxText()
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        for method in methods:
            self.method_combo.append_text(method)
        self.method_combo.set_active(0)
        self.method_combo.set_size_request(120, -1)
        url_box.append(self.method_combo)

        # URL entry
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("https://api.example.com/endpoint")
        self.url_entry.set_hexpand(True)
        self.url_entry.connect('activate', self.on_send_clicked)
        url_box.append(self.url_entry)

        # Quick send button
        quick_send_btn = Gtk.Button.new_with_label("🚀")
        quick_send_btn.set_tooltip_text("Send Request")
        quick_send_btn.connect('clicked', self.on_send_clicked)
        url_box.append(quick_send_btn)

        url_group.add(url_box)
        parent.append(url_group)

    def setup_headers_section(self, parent):
        """Setup expandable headers section"""
        self.headers_panel = HeadersPanel()

        headers_expander = Adw.ExpanderRow()
        headers_expander.set_title("Headers")
        headers_expander.set_subtitle("Request headers (optional)")
        headers_expander.add_row(self.headers_panel)
        headers_expander.set_expanded(False)

        headers_group = Adw.PreferencesGroup()
        headers_group.add(headers_expander)
        parent.append(headers_group)

    def setup_request_panel(self):
        """Setup request body editor"""
        request_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(6)
        toolbar.set_margin_start(12)
        toolbar.set_margin_end(12)

        format_btn = Gtk.Button.new_with_label("Format Body")
        format_btn.set_tooltip_text("Format request body")
        format_btn.connect('clicked', self.on_format_request)
        toolbar.append(format_btn)

        minify_btn = Gtk.Button.new_with_label("Minify Body")
        minify_btn.set_tooltip_text("Minify request body")
        minify_btn.connect('clicked', self.on_minify_request)
        toolbar.append(minify_btn)

        clear_btn = Gtk.Button.new_with_label("Clear Body")
        clear_btn.set_tooltip_text("Clear request body")
        clear_btn.connect('clicked', self.on_clear_body)
        toolbar.append(clear_btn)

        request_box.append(toolbar)

        # Request body editor
        self.body_text = self.syntax_highlighter.create_source_view('json')
        self.body_text.set_margin_start(12)
        self.body_text.set_margin_end(12)
        self.body_text.set_margin_bottom(12)
        self.body_text.set_vexpand(True)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.body_text)
        scrolled.set_vexpand(True)
        request_box.append(scrolled)

        return request_box

    def setup_response_panel(self):
        """Setup response viewer"""
        response_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(6)
        toolbar.set_margin_start(12)
        toolbar.set_margin_end(12)

        format_btn = Gtk.Button.new_with_label("Format")
        format_btn.set_tooltip_text("Format response content")
        format_btn.connect('clicked', self.on_format_response)
        toolbar.append(format_btn)

        minify_btn = Gtk.Button.new_with_label("Minify")
        minify_btn.set_tooltip_text("Minify response content")
        minify_btn.connect('clicked', self.on_minify_response)
        toolbar.append(minify_btn)

        search_btn = Gtk.Button.new_with_label("Search")
        search_btn.set_tooltip_text("Search in response (Ctrl+F)")
        search_btn.connect('clicked', self.on_search_response)
        toolbar.append(search_btn)

        # Search panel
        self.response_text = self.syntax_highlighter.create_source_view()
        self.response_text.set_editable(False)
        self.response_text.set_margin_start(12)
        self.response_text.set_margin_end(12)
        self.response_text.set_margin_bottom(12)
        self.response_text.set_vexpand(True)

        self.search_panel = SearchPanel(self.response_text)
        self.search_panel.set_visible(False)
        toolbar.append(self.search_panel)

        response_box.append(toolbar)

        # Status bar
        self.setup_status_bar(response_box)

        # Response viewer
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.response_text)
        scrolled.set_vexpand(True)
        response_box.append(scrolled)

        return response_box

    def setup_status_bar(self, parent):
        """Setup status bar at bottom of response panel"""
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        status_box.set_margin_top(12)
        status_box.set_margin_start(12)
        status_box.set_margin_end(12)

        self.status_label = Gtk.Label(label="Ready to send requests")
        self.status_label.add_css_class('title-4')
        status_box.append(self.status_label)

        self.time_label = Gtk.Label(label="")
        self.time_label.add_css_class('dim-label')
        status_box.append(self.time_label)

        self.size_label = Gtk.Label(label="")
        self.size_label.add_css_class('dim-label')
        status_box.append(self.size_label)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        self.progress_bar.set_hexpand(True)
        status_box.append(self.progress_bar)

        parent.append(status_box)

    def setup_actions(self):
        """Setup window-level actions"""
        # Window actions
        actions = [
            ('send_request', self.on_send_clicked),
            ('find_in_response', self.on_search_response),
            ('export_response', self.on_export),
            ('new_request', self.on_new_request),
            ('show-help-overlay', self.show_shortcuts),
        ]

        for name, callback in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect('activate', callback)
            self.add_action(action)

        # Example actions
        example_actions = [
            ('example_jsonplaceholder_get', 'jsonplaceholder_get'),
            ('example_github_get', 'github_get'),
            ('example_randomuser_get', 'randomuser_get'),
            ('example_jsonplaceholder_post', 'jsonplaceholder_post'),
            ('example_httpbin_post', 'httpbin_post'),
            ('example_xml', 'xml_example'),
            ('example_html', 'html_example')
        ]

        for action_name, example_type in example_actions:
            app_action = self.get_application().lookup_action(action_name)
            if app_action:
                app_action.connect('activate', lambda action, param, et=example_type: self.load_example(et))

    def apply_initial_settings(self):
        """Apply saved settings after UI is fully loaded"""
        # Apply SSL setting
        ssl_verify = self.settings_manager.get_ssl_verification()
        self.request_handler.set_ssl_verification(ssl_verify)

        # Apply theme and font settings
        self.settings_manager.apply_initial_settings()

        # Apply CSS classes to code editors
        self.apply_css_classes()

    def apply_css_classes(self):
        """Apply CSS classes to code editors for theming"""
        if hasattr(self, 'body_text'):
            self.body_text.add_css_class('code-font')
            self.body_text.add_css_class('code-view')

        if hasattr(self, 'response_text'):
            self.response_text.add_css_class('code-font')
            self.response_text.add_css_class('code-view')

    # Event Handlers
    def on_preferences(self, button):
        """Open preferences window"""
        if not self.preferences_window:
            self.preferences_window = PreferencesWindow(self, self.settings_manager)
            self.preferences_window.connect('close-request', self.on_preferences_close_request)
        self.preferences_window.present()

    def on_preferences_close_request(self, window):
        """Handle preferences window close"""
        self.preferences_window = None
        return False  # Allow window to close

    def on_send_clicked(self, widget=None, action=None, param=None):
        """Send API request"""
        method = self.method_combo.get_active_text()
        url = self.url_entry.get_text()

        if not url:
            self.show_toast("Please enter a URL")
            return

        if not self.request_handler.validate_url(url):
            self.show_toast("Please enter a valid URL")
            return

        # UI loading state
        self.status_label.set_label(f"Sending {method} request...")
        self.time_label.set_label("")
        self.size_label.set_label("")
        self.send_btn.set_sensitive(False)
        self.progress_bar.set_visible(True)
        self.progress_bar.pulse()

        # Gather request data
        headers = self.headers_panel.get_headers()
        body_buffer = self.body_text.get_buffer()
        body_text = body_buffer.get_text(body_buffer.get_start_iter(), body_buffer.get_end_iter(), True)
        content_type = headers.get('Content-Type', 'application/json')

        # BASİT ÇÖZÜM: Thread kullan, ama UI güncellemeleri main thread'de yap
        import threading

        def execute_in_thread():
            # İsteği thread içinde yap
            response = self.request_handler.send_request(method, url, headers, body_text, content_type)
            # UI güncellemesini main thread'e gönder
            GLib.idle_add(self.handle_response, response)

        thread = threading.Thread(target=execute_in_thread)
        thread.daemon = True
        thread.start()

    def handle_response(self, response: Dict[str, Any]):
        self.send_btn.set_sensitive(True)
        self.progress_bar.set_visible(False)

        if 'error' in response:
            self.status_label.set_label("❌ Request Failed")
            self.time_label.set_label("")
            self.size_label.set_label("")

            buffer = self.response_text.get_buffer()
            buffer.set_text(response['error'])
            buffer.set_language(self.syntax_highlighter.language_manager.get_language('text'))
        else:
            status_code = response['status_code']
            status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"

            self.status_label.set_label(f"{status_emoji} {status_code} {response.get('reason', '')}")
            self.time_label.set_label(f"⏱️ {response['response_time']}ms")
            self.size_label.set_label(f"📦 {response['size']} bytes")

            # Update response body
            buffer = self.response_text.get_buffer()
            self.last_content_type = response['headers'].get('Content-Type', '')
            formatted = self.formatter.format_content(response['body'], self.last_content_type)
            buffer.set_text(formatted)

            # Apply syntax highlighting
            language = self.syntax_highlighter.detect_language(response['body'], self.last_content_type)
            lang = self.syntax_highlighter.language_manager.get_language(language)
            if lang:
                buffer.set_language(lang)

        # Add to history
        method = self.method_combo.get_active_text()
        url = self.url_entry.get_text()
        body_buffer = self.body_text.get_buffer()
        body_text = body_buffer.get_text(body_buffer.get_start_iter(), body_buffer.get_end_iter(), True)
        headers = self.headers_panel.get_headers()

        self.history_manager.add_to_history(method, url, response, body_text, headers)

    def handle_response(self, response: Dict[str, Any]):
        """Handle request response - MUST be called from main thread"""
        # UI updates must happen in main thread
        def update_ui():
            self.send_btn.set_sensitive(True)
            self.progress_bar.set_visible(False)

            if 'error' in response:
                self.status_label.set_label("❌ Request Failed")
                self.time_label.set_label("")
                self.size_label.set_label("")

                buffer = self.response_text.get_buffer()
                buffer.set_text(response['error'])
                buffer.set_language(self.syntax_highlighter.language_manager.get_language('text'))
            else:
                status_code = response['status_code']
                status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"

                self.status_label.set_label(f"{status_emoji} {status_code} {response.get('reason', '')}")
                self.time_label.set_label(f"⏱️ {response['response_time']}ms")
                self.size_label.set_label(f"📦 {response['size']} bytes")

                # Update response body
                buffer = self.response_text.get_buffer()
                self.last_content_type = response['headers'].get('Content-Type', '')
                formatted = self.formatter.format_content(response['body'], self.last_content_type)
                buffer.set_text(formatted)

                # Apply syntax highlighting
                language = self.syntax_highlighter.detect_language(response['body'], self.last_content_type)
                lang = self.syntax_highlighter.language_manager.get_language(language)
                if lang:
                    buffer.set_language(lang)

            # Add to history
            method = self.method_combo.get_active_text()
            url = self.url_entry.get_text()
            body_buffer = self.body_text.get_buffer()
            body_text = body_buffer.get_text(body_buffer.get_start_iter(), body_buffer.get_end_iter(), True)
            headers = self.headers_panel.get_headers()

            self.history_manager.add_to_history(method, url, response, body_text, headers)

        # Ensure UI updates happen in main thread
        GLib.idle_add(update_ui)

    def load_example(self, example_type: str):
        """Load API example"""
        example = self.examples_manager.get_example(example_type)
        if example:
            # Set method
            for i, method in enumerate(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']):
                if method == example['method']:
                    self.method_combo.set_active(i)
                    break

            # Set URL and body
            self.url_entry.set_text(example['url'])

            buffer = self.body_text.get_buffer()
            buffer.set_text(example['body'])

            # Apply syntax highlighting
            self.syntax_highlighter.set_content(self.body_text, example['body'])

    def on_history_activated(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow):
        """Handle history item selection"""
        request_key = self.history_manager.get_request_key_from_row(row)
        if not request_key:
            return

        data = self.history_manager.get_history_data(request_key)
        if not data:
            return

        self._load_history_item(data)

    def _load_history_item(self, data: Dict[str, Any]):
        """Load history item into UI"""
        # Load request data
        for i, method in enumerate(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']):
            if method == data['method']:
                self.method_combo.set_active(i)
                break

        self.url_entry.set_text(data['url'])

        buffer = self.body_text.get_buffer()
        buffer.set_text(data['body'])

        # Load response data
        response_buffer = self.response_text.get_buffer()
        content_type = data['response']['headers'].get('Content-Type', '')
        formatted = self.formatter.format_content(data['response']['body'], content_type)
        response_buffer.set_text(formatted)

        # Update status
        status_code = data['response']['status_code']
        status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"

        self.status_label.set_label(f"{status_emoji} {status_code}")
        self.time_label.set_label(f"⏱️ {data['response']['response_time']}ms")
        self.size_label.set_label(f"📦 {data['response']['size']} bytes")

    # Toolbar actions
    def on_format_request(self, button):
        buffer = self.body_text.get_buffer()
        content = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        if not content.strip():
            return

        content_type = 'application/json'
        if hasattr(self, 'headers_panel'):
            headers = self.headers_panel.get_headers()
            content_type = headers.get('Content-Type', content_type)

        formatted = self.formatter.format_content(content, content_type)
        buffer.set_text(formatted)

    def on_minify_request(self, button):
        buffer = self.body_text.get_buffer()
        content = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        if not content.strip():
            return

        content_type = 'application/json'
        if hasattr(self, 'headers_panel'):
            headers = self.headers_panel.get_headers()
            content_type = headers.get('Content-Type', content_type)

        minified = self.formatter.minify_content(content, content_type)
        buffer.set_text(minified)

    def on_clear_body(self, button):
        buffer = self.body_text.get_buffer()
        buffer.set_text("")

    def on_format_response(self, button):
        buffer = self.response_text.get_buffer()
        content = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        if not content.strip():
            return

        formatted = self.formatter.format_content(content, self.last_content_type)
        buffer.set_text(formatted)

    def on_minify_response(self, button):
        buffer = self.response_text.get_buffer()
        content = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        if not content.strip():
            return

        minified = self.formatter.minify_content(content, self.last_content_type)
        buffer.set_text(minified)

    def on_search_response(self, button=None, action=None, param=None):
        if self.search_panel:
            self.search_panel.set_visible(not self.search_panel.get_visible())
            if self.search_panel.get_visible():
                self.search_panel.search_entry.grab_focus()

    def on_clear_history(self, button):
        self.history_manager.clear_history()

    def on_new_request(self, widget=None, action=None, param=None):
        self.url_entry.set_text("")

        body_buffer = self.body_text.get_buffer()
        body_buffer.set_text("")

        response_buffer = self.response_text.get_buffer()
        response_buffer.set_text("")

        self.status_label.set_label("Ready to send requests")
        self.time_label.set_label("")
        self.size_label.set_label("")

    def on_export(self, widget=None, action=None, param=None):
        buffer = self.response_text.get_buffer()
        response_text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

        if not response_text.strip():
            self.show_toast("No response to export")
            return

        dialog = Gtk.FileChooserNative(
            title="Export Response",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE
        )

        dialog.set_modal(True)
        dialog.connect('response', self.on_export_response, response_text)
        dialog.show()

    def on_export_response(self, dialog: Gtk.FileChooserNative, response_id: Gtk.ResponseType, response_text: str):
        if response_id == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                filename: Optional[str] = file.get_path()
                if filename:
                    try:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response_text)
                        self.show_toast(f"Response exported to {os.path.basename(filename)}")
                    except Exception as e:
                        self.show_toast(f"Export failed: {str(e)}")

        dialog.destroy()

    def show_toast(self, message: str):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.present()

    def show_shortcuts(self, action=None, param=None):
        dialog = Gtk.Dialog(
            title="Rappit - Keyboard Shortcuts",
            transient_for=self,
            modal=True
        )

        dialog.add_button("_Close", Gtk.ResponseType.CLOSE)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)

        shortcuts_text = """
        <b>General Shortcuts:</b>

        <b>Ctrl + N</b> - New Request
        <b>Ctrl + Enter</b> - Send Request
        <b>Ctrl + F</b> - Find in Response
        <b>Ctrl + E</b> - Export Response
        <b>Ctrl + Q</b> - Quit Application

        <b>Request Editing:</b>

        <b>Enter</b> - Send request (when in URL field)
        <b>Tab</b> - Next field
        <b>Shift + Tab</b> - Previous field
        """

        label = Gtk.Label()
        label.set_markup(shortcuts_text)
        label.set_wrap(True)
        label.set_justify(Gtk.Justification.LEFT)

        content.append(label)
        dialog.get_content_area().append(content)
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.present()
