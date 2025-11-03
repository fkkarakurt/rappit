import json
import xml.dom.minidom
import re
from html import escape

class Formatter:
    """
    A sophisticated content formatter that supports JSON, XML, and HTML formatting.
    Provides automatic content type detection and both formatting and minification capabilities.
    """

    def __init__(self):
        """Initialize the Formatter instance."""
        pass

    def format_content(self, content: str, content_type: str = None) -> str:
        """
        Format content based on content type or automatic detection.

        Args:
            content (str): The content to be formatted
            content_type (str, optional): Explicit content type hint. Defaults to None.

        Returns:
            str: Formatted content, or original content if formatting fails or not applicable
        """
        if not content or not content.strip():
            return content

        content = content.strip()

        # Primary formatting based on explicit content type
        if content_type:
            if 'json' in content_type:
                result = self.format_json(content)
                if not result.startswith('/* JSON Format Error'):
                    return result
            elif 'xml' in content_type:
                result = self.format_xml(content)
                if not result.startswith('<!-- XML Format Error'):
                    return result
            elif 'html' in content_type:
                result = self.format_html(content)
                if not result.startswith('<!-- HTML Format Error'):
                    return result

        # Secondary formatting based on automatic content type detection
        if self._is_json(content):
            return self.format_json(content)
        elif self._is_xml(content):
            return self.format_xml(content)
        elif self._is_html(content):
            return self.format_html(content)

        return content

    def _is_json(self, content: str) -> bool:
        """
        Advanced JSON content detection with pattern matching and validation.

        Args:
            content (str): Content to check for JSON format

        Returns:
            bool: True if content appears to be JSON, False otherwise
        """
        content = content.strip()
        if not content:
            return False

        # Basic JSON structural patterns
        json_patterns = [
            (content.startswith('{') and content.endswith('}')),
            (content.startswith('[') and content.endswith(']'))
        ]

        if any(json_patterns):
            try:
                # Attempt to parse as valid JSON
                json.loads(content)
                return True
            except:
                # Fallback: Check for JSON-like patterns in partial/invalid JSON
                if '"' in content and (':' in content or '[' in content or '{' in content):
                    return True
        return False

    def _is_xml(self, content: str) -> bool:
        """
        Advanced XML content detection with tag pattern analysis.

        Args:
            content (str): Content to check for XML format

        Returns:
            bool: True if content appears to be XML, False otherwise
        """
        content = content.strip()
        if not content:
            return False

        # XML declaration and common root element patterns
        xml_patterns = [
            content.startswith('<?xml'),
            content.startswith('<soap:'),
            content.startswith('<rss'),
            content.startswith('<feed'),
            re.match(r'^<[a-zA-Z][a-zA-Z0-9]*[>\\s]', content) is not None
        ]

        # Validate by checking for opening/closing tag structure
        if any(xml_patterns):
            open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)(?:\s|>)', content)
            close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', content)
            return len(open_tags) > 0 or len(close_tags) > 0

        return False

    def _is_html(self, content: str) -> bool:
        """
        Advanced HTML content detection using common HTML element patterns.

        Args:
            content (str): Content to check for HTML format

        Returns:
            bool: True if content appears to be HTML, False otherwise
        """
        content_lower = content.lower().strip()
        if not content_lower:
            return False

        # Common HTML document and element patterns
        html_patterns = [
            '<!doctype html' in content_lower,
            '<html' in content_lower,
            '<head' in content_lower,
            '<body' in content_lower,
            '<div' in content_lower,
            '<p>' in content_lower,
            '<span' in content_lower,
            '<h1' in content_lower or '<h2' in content_lower,
            '<table' in content_lower,
            '<style' in content_lower,
            '<script' in content_lower
        ]

        return any(html_patterns)

    def format_json(self, content: str) -> str:
        """
        Advanced JSON formatting with error handling and partial correction.

        Args:
            content (str): JSON content to format

        Returns:
            str: Beautifully formatted JSON or error message with original content
        """
        try:
            parsed = json.loads(content)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            # Attempt partial correction for common JSON issues
            try:
                # Remove trailing commas that break JSON parsing
                content = re.sub(r',\s*}', '}', content)
                content = re.sub(r',\s*]', ']', content)
                parsed = json.loads(content)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except:
                return f"/* JSON Format Error: {str(e)} */\n{content}"
        except Exception as e:
            return f"/* JSON Format Error: {str(e)} */\n{content}"

    def format_xml(self, content: str) -> str:
        """
        Advanced XML formatting with proper indentation and structure.

        Args:
            content (str): XML content to format

        Returns:
            str: Formatted XML or error message with original content
        """
        try:
            content = content.strip()

            # Add XML declaration if missing
            if not content.startswith('<?xml'):
                content = '<?xml version="1.0" encoding="UTF-8"?>\n' + content

            # Use xml.dom.minidom for professional XML formatting
            parsed = xml.dom.minidom.parseString(content)
            formatted = parsed.toprettyxml(indent="  ")

            # Clean up excessive empty lines
            lines = [line for line in formatted.split('\n') if line.strip()]
            return '\n'.join(lines)

        except Exception as e:
            # Fallback to simple XML formatting if standard method fails
            try:
                return self._simple_xml_format(content)
            except:
                return f"<!-- XML Format Error: {str(e)} -->\n{content}"

    def _simple_xml_format(self, content: str) -> str:
        """
        Robust fallback XML formatting with manual indentation logic.

        Args:
            content (str): XML content to format

        Returns:
            str: Manually formatted XML with proper indentation
        """
        # Separate tags onto new lines for proper formatting
        content = re.sub(r'>\s*<', '>\n<', content)
        lines = content.split('\n')
        formatted = []
        indent_level = 0
        in_tag = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # XML declaration - no indentation
            if line.startswith('<?xml'):
                formatted.append(line)
                continue

            # Closing tag - decrease indentation
            if line.startswith('</'):
                indent_level = max(0, indent_level - 1)
                formatted.append('  ' * indent_level + line)
            # Self-closing tag - maintain current indentation
            elif line.endswith('/>'):
                formatted.append('  ' * indent_level + line)
            # Opening tag - apply indentation and potentially increase level
            elif line.startswith('<') and not line.startswith('</'):
                formatted.append('  ' * indent_level + line)
                # Increase indentation if this is not a self-closing tag
                if not line.endswith('/>') and '</' not in line:
                    indent_level += 1
            # Text content - maintain current indentation
            else:
                formatted.append('  ' * indent_level + line)

        return '\n'.join(formatted)

    def format_html(self, content: str) -> str:
        """
        Advanced HTML formatting with proper element handling.

        Args:
            content (str): HTML content to format

        Returns:
            str: Formatted HTML or error message with original content
        """
        try:
            return self._simple_html_format(content)
        except Exception as e:
            return f"<!-- HTML Format Error: {str(e)} -->\n{content}"

    def _simple_html_format(self, content: str) -> str:
        """
        Sophisticated HTML formatting with void element awareness.

        Args:
            content (str): HTML content to format

        Returns:
            str: Properly formatted HTML with correct indentation
        """
        # Separate tags for individual processing
        content = re.sub(r'>\s*<', '>\n<', content)
        lines = content.split('\n')
        formatted = []
        indent_level = 0

        # HTML5 void elements (self-closing, no closing tag needed)
        void_elements = ['area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                        'input', 'link', 'meta', 'param', 'source', 'track', 'wbr']

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Doctype declaration - no indentation
            if line.lower().startswith('<!doctype'):
                formatted.append(line)
                continue

            # HTML comments - maintain current indentation
            if line.startswith('<!--'):
                formatted.append('  ' * indent_level + line)
                continue

            # Closing tag - decrease indentation level
            if line.startswith('</'):
                indent_level = max(0, indent_level - 1)
                formatted.append('  ' * indent_level + line)
            # Self-closing or void element - maintain indentation
            elif any(line.rstrip().endswith(f'</{tag}>') for tag in void_elements) or line.endswith('/>'):
                formatted.append('  ' * indent_level + line)
            # Opening tag - apply indentation and conditionally increase level
            elif line.startswith('<') and not line.startswith('</'):
                formatted.append('  ' * indent_level + line)
                # Extract tag name to check if it's a void element
                tag_name = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)', line)
                if tag_name and tag_name.group(1).lower() not in void_elements and not line.endswith('/>'):
                    # Only increase indentation if this is not an inline element
                    if f"</{tag_name.group(1)}>" not in line:
                        indent_level += 1
            # Text content or other elements
            else:
                formatted.append('  ' * indent_level + line)

        return '\n'.join(formatted)

    def minify_content(self, content: str, content_type: str = None) -> str:
        """
        Minify content by removing unnecessary whitespace and comments.

        Args:
            content (str): Content to minify
            content_type (str, optional): Explicit content type hint. Defaults to None.

        Returns:
            str: Minified content, or original content if minification not applicable
        """
        if not content:
            return content

        # JSON minification
        if self._is_json(content) or (content_type and 'json' in content_type):
            try:
                parsed = json.loads(content)
                return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
            except:
                pass

        # XML/HTML minification
        elif self._is_xml(content) or self._is_html(content):
            # Remove comments and compress whitespace
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'>\s+<', '><', content)
            return content.strip()

        return content
