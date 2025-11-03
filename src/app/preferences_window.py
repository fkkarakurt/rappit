# src/app/preferences_window.py
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio

class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, parent, settings_manager):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.settings_manager = settings_manager
        self.parent = parent

        self.set_title("Preferences")
        self.set_default_size(600, 700)

        # Track if window is being closed
        self._is_closing = False

        self.setup_ui()

    def setup_ui(self):
        # Appearance Page
        appearance_page = Adw.PreferencesPage()
        appearance_page.set_title("Appearance")
        appearance_page.set_icon_name("applications-graphics-symbolic")

        # Theme Section
        theme_group = Adw.PreferencesGroup()
        theme_group.set_title("Theme")
        theme_group.set_description("Choose application theme")

        theme_row = Adw.ComboRow()
        theme_row.set_title("Theme")
        theme_list = Gtk.StringList.new([
            self.settings_manager.themes['system'],
            self.settings_manager.themes['light'],
            self.settings_manager.themes['dark']
        ])
        theme_row.set_model(theme_list)

        current_theme = self.settings_manager.get_theme()
        theme_keys = list(self.settings_manager.themes.keys())
        theme_index = theme_keys.index(current_theme)
        theme_row.set_selected(theme_index)
        theme_row.connect('notify::selected', self.on_theme_changed)
        theme_group.add(theme_row)

        # Font Section
        font_group = Adw.PreferencesGroup()
        font_group.set_title("Font")
        font_group.set_description("Customize editor fonts")

        # Font Preview
        self.font_preview = Gtk.Label()
        self.font_preview.set_text("ABCdef123 - Font Preview")
        self.font_preview.set_margin_top(12)
        self.font_preview.set_margin_bottom(12)
        self.font_preview.set_xalign(0)
        font_group.add(self.font_preview)

        # Font Family
        font_family_row = Adw.ComboRow()
        font_family_row.set_title("Font Family")
        font_list = Gtk.StringList.new([
            self.settings_manager.font_families[family]
            for family in self.settings_manager.font_families
        ])
        font_family_row.set_model(font_list)

        current_font = self.settings_manager.get_font_family()
        font_keys = list(self.settings_manager.font_families.keys())
        font_index = font_keys.index(current_font)
        font_family_row.set_selected(font_index)
        font_family_row.connect('notify::selected', self.on_font_family_changed)
        font_group.add(font_family_row)

        # Font Size
        font_size_row = Adw.ComboRow()
        font_size_row.set_title("Font Size")
        size_list = Gtk.StringList.new([f"{size} px" for size in self.settings_manager.font_sizes])
        font_size_row.set_model(size_list)

        current_size = self.settings_manager.get_font_size()
        size_index = self.settings_manager.font_sizes.index(current_size)
        font_size_row.set_selected(size_index)
        font_size_row.connect('notify::selected', self.on_font_size_changed)
        font_group.add(font_size_row)

        appearance_page.add(theme_group)
        appearance_page.add(font_group)

        # Behavior Page
        behavior_page = Adw.PreferencesPage()
        behavior_page.set_title("Behavior")
        behavior_page.set_icon_name("emblem-system-symbolic")

        # Request Section
        request_group = Adw.PreferencesGroup()
        request_group.set_title("Requests")

        # SSL Verification
        self.ssl_verify_switch = Adw.SwitchRow()
        self.ssl_verify_switch.set_title("SSL Certificate Verification")
        self.ssl_verify_switch.set_subtitle("Verify SSL certificates for HTTPS requests (recommended for security)")
        self.ssl_verify_switch.set_active(self.settings_manager.get_ssl_verification())
        self.ssl_verify_switch.connect('notify::active', self.on_ssl_verify_changed)
        request_group.add(self.ssl_verify_switch)

        self.auto_format_switch = Adw.SwitchRow()
        self.auto_format_switch.set_title("Auto-format responses")
        self.auto_format_switch.set_subtitle("Automatically format JSON/XML responses")
        self.auto_format_switch.set_active(self.settings_manager.settings.get_boolean('auto-format-response'))
        self.auto_format_switch.connect('notify::active', self.on_auto_format_changed)
        request_group.add(self.auto_format_switch)

        # History Section
        history_group = Adw.PreferencesGroup()
        history_group.set_title("History")

        self.save_history_switch = Adw.SwitchRow()
        self.save_history_switch.set_title("Save request history")
        self.save_history_switch.set_active(self.settings_manager.settings.get_boolean('save-history'))
        self.save_history_switch.connect('notify::active', self.on_save_history_changed)
        history_group.add(self.save_history_switch)

        behavior_page.add(request_group)
        behavior_page.add(history_group)

        self.add(appearance_page)
        self.add(behavior_page)

        # Update font preview
        self.update_font_preview()

    def update_font_preview(self):
        """Update font preview with current settings"""
        font_family = self.settings_manager.get_font_family()
        font_size = self.settings_manager.get_font_size()

        if font_family != 'system':
            font_name = self.settings_manager.get_font_display_name(font_family)
            font_desc = f"{font_name}, {font_size}px"
            preview_text = f"ABCdef123 - {font_desc}"
        else:
            font_desc = f"System, {font_size}px"
            preview_text = f"ABCdef123 - {font_desc}"

        # Test if font is available
        available_fonts = ["Inter", "Fira Code", "JetBrains Mono", "Roboto Mono",
                          "Source Code Pro", "Ubuntu Mono", "Monospace", "Courier New"]

        if font_family != 'system' and self.settings_manager.get_font_display_name(font_family) not in available_fonts:
            preview_text += " (Font not available)"

        self.font_preview.set_markup(f"<span font='{font_desc}'>{preview_text}</span>")

    def on_theme_changed(self, row, param):
        """Handle theme change - debounced to prevent rapid updates"""
        if self._is_closing:
            return

        theme_keys = list(self.settings_manager.themes.keys())
        selected_index = row.get_selected()
        if 0 <= selected_index < len(theme_keys):
            self.settings_manager.set_theme(theme_keys[selected_index])

    def on_font_family_changed(self, row, param):
        """Handle font family change"""
        if self._is_closing:
            return

        font_keys = list(self.settings_manager.font_families.keys())
        selected_index = row.get_selected()
        if 0 <= selected_index < len(font_keys):
            self.settings_manager.set_font_family(font_keys[selected_index])
            self.update_font_preview()

    def on_font_size_changed(self, row, param):
        """Handle font size change"""
        if self._is_closing:
            return

        selected_index = row.get_selected()
        if 0 <= selected_index < len(self.settings_manager.font_sizes):
            self.settings_manager.set_font_size(self.settings_manager.font_sizes[selected_index])
            self.update_font_preview()

    def on_ssl_verify_changed(self, switch, param):
        """Handle SSL verification setting change"""
        if self._is_closing:
            return

        verify_ssl = switch.get_active()
        self.settings_manager.set_ssl_verification(verify_ssl)

        # Apply to request handler
        if hasattr(self.parent, 'request_handler'):
            self.parent.request_handler.set_ssl_verification(verify_ssl)

    def on_auto_format_changed(self, switch, param):
        """Handle auto-format setting change"""
        if self._is_closing:
            return

        self.settings_manager.settings.set_boolean('auto-format-response', switch.get_active())

    def on_save_history_changed(self, switch, param):
        """Handle save history setting change"""
        if self._is_closing:
            return

        self.settings_manager.settings.set_boolean('save-history', switch.get_active())

    def do_close_request(self):
        """Override close request to handle cleanup properly"""
        self._is_closing = True
        # Notify parent that window is closing
        if hasattr(self.parent, 'preferences_window'):
            self.parent.preferences_window = None
        return False  # Let the window close normally
