import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, Gdk
import os

class SettingsManager:
    """
    Manages application settings including themes, fonts, and UI preferences.
    Applies settings to the entire application.
    """

    def __init__(self):
        self.settings = Gio.Settings.new('io.github.fkkarakurt.rappit')

        # Available themes
        self.themes = {
            'system': 'System Default',
            'light': 'Light',
            'dark': 'Dark'
        }

        # Available font families with proper font names
        self.font_families = {
            'source-code-pro': 'Source Code Pro',
            'ubuntu-mono': 'Ubuntu Mono',
            'monospace': 'Monospace',
            'courier-new': 'Courier New'
        }

        # Font sizes
        self.font_sizes = [10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24]

        # CSS providers
        self.css_provider = Gtk.CssProvider()
        self.current_css = ""

    def get_theme(self) -> str:
        return self.settings.get_string('theme')

    def set_theme(self, theme: str):
        self.settings.set_string('theme', theme)
        self.apply_theme(theme)

    def get_font_family(self) -> str:
        return self.settings.get_string('font-family')

    def set_font_family(self, font_family: str):
        self.settings.set_string('font-family', font_family)
        self.apply_font_settings()

    def get_font_size(self) -> int:
        return self.settings.get_int('font-size')

    def set_font_size(self, font_size: int):
        self.settings.set_int('font-size', font_size)
        self.apply_font_settings()

    def get_ssl_verification(self) -> bool:
        return self.settings.get_boolean('ssl-verification')

    def set_ssl_verification(self, verify: bool):
        self.settings.set_boolean('ssl-verification', verify)

    def apply_theme(self, theme: str):
        """Apply theme to the entire application"""
        style_manager = Adw.StyleManager.get_default()

        if theme == 'dark':
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif theme == 'light':
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def apply_font_settings(self):
        """Apply font settings to the entire application"""
        font_family = self.get_font_family()
        font_size = self.get_font_size()

        # Remove previous CSS
        display = Gdk.Display.get_default()
        Gtk.StyleContext.remove_provider_for_display(display, self.css_provider)

        if font_family != 'system':
            font_name = self.get_font_display_name(font_family)
            css = f"""
            /* Application-wide settings */
            * {{
                font-family: '{font_name}', sans-serif;
                font-size: {font_size}px;
            }}

            /* Code editors and monospace areas */
            .code-font, .code-view, .monospace {{
                font-family: '{font_name}', monospace;
            }}

            /* Source views specifically */
            GtkSourceView {{
                font-family: '{font_name}', monospace;
                font-size: {font_size}px;
            }}

            /* Ensure all text areas use the font */
            textview, entry, label, button {{
                font-family: '{font_name}', sans-serif;
                font-size: {font_size}px;
            }}
            """
        else:
            css = f"""
            /* System fonts with custom size */
            * {{
                font-size: {font_size}px;
            }}

            .code-font, .code-view, .monospace, GtkSourceView {{
                font-size: {font_size}px;
            }}
            """

        self.current_css = css
        try:
            self.css_provider.load_from_data(css.encode(), -1)
            Gtk.StyleContext.add_provider_for_display(
                display,
                self.css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"CSS loading error: {e}")

    def get_font_display_name(self, font_family: str) -> str:
        """Get display name for font family"""
        font_map = {
            'inter': 'Inter',
            'fira-code': 'Fira Code',
            'jetbrains-mono': 'JetBrains Mono',
            'roboto-mono': 'Roboto Mono',
            'source-code-pro': 'Source Code Pro',
            'ubuntu-mono': 'Ubuntu Mono',
            'monospace': 'Monospace',
            'courier-new': 'Courier New'
        }
        return font_map.get(font_family, 'Monospace')

    def apply_initial_settings(self):
        """Apply all settings on application start"""
        self.apply_theme(self.get_theme())
        self.apply_font_settings()
