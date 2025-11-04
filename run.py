#!/usr/bin/env python3
"""
Rappit Application Entry Point
------------------------------
This script serves as the main entry point for the Rappit application.
It ensures that the project's source directory is correctly added to the
system path before attempting to import and run the main GTK application class.
"""
import sys
import os

# Define the root directory of the project, relative to this script's location.
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')

# CRITICAL: Add the 'src' directory to the system path to allow module imports
# such as 'from app.main import RappitApplication' to resolve correctly.
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Flatpak compatibility
if 'FLATPAK_ID' in os.environ:
    # Flatpak environment
    resource_path = '/app/bin/src'
    if resource_path not in sys.path:
        sys.path.insert(0, resource_path)
    print("🔧 Flatpak environment detected")

try:
    # Attempt to import the core GTK Application class.
    from app.main import RappitApplication
except ImportError as e:
    # Handle critical import errors and provide debugging context for the user.
    print(f"❌ Critical Import Error: {e}")
    print("📁 Current working directory:", project_root)
    print("📁 Current working directory contents:", os.listdir(project_root))
    if os.path.exists(os.path.join(project_root, 'src')):
        print("📁 'src' directory contents:", os.listdir(os.path.join(project_root, 'src')))
    else:
        print("❌ 'src' directory not found")

    # Flatpak environment
    if 'FLATPAK_ID' in os.environ:
        print("🔧 Flatpak paths:")
        print("   /app contents:", os.listdir('/app') if os.path.exists('/app') else "/app not found")
        print("   /app/bin contents:", os.listdir('/app/bin') if os.path.exists('/app/bin') else "/app/bin not found")

    sys.exit(1)

def main():
    """
    Initializes and executes the Rappit GTK Application.
    """
    print("🚀 Initializing and launching Rappit application...")
    # Instantiate the main application class
    app = RappitApplication()

    # Run the application with command-line arguments and return the exit code
    return app.run(sys.argv)

if __name__ == '__main__':
    # Execute the main function when the script is run directly
    sys.exit(main())
