# Defines the project name, language, and global options.
project('rappit', 'python',
    version: 'v1.0',
    license: 'AGPL-3.0',
    meson_version: '>=0.50.0',
    default_options: [
        'python.install_env=auto',
        'buildtype=release'
    ]
)

# --- Configuration Variables ---
app_id = 'io.github.fkkarakurt.rappit'
datadir = get_option('datadir')
bindir = get_option('bindir')
app_datadir = datadir / app_id
pkgdatadir = get_option('prefix') / app_datadir

# --- Dependencies ---
python = import('python').find_installation('python3')

# GTK and GNOME dependencies
pygobject = dependency('pygobject-3.0', version: '>=3.42.0')
pycairo = dependency('pycairo', version: '>=1.16.0')
gtk4 = dependency('gtk4', version: '>=4.0.0')
libadwaita = dependency('libadwaita-1', version: '>=1.0.0')
gtksource = dependency('gtksourceview-5', version: '>=5.0.0')

# GLib schemas for settings
gnome = import('gnome')

# Check for required Python modules
python.check_dependency('requests', version: '>=2.25.0')
python.check_dependency('pygments', version: '>=2.7.0')

# --- Compile GSettings schemas ---
gnome.compile_schemas()

# --- Installation Steps ---

# 1. Install the main execution script
install_data(
    'run.py',
    install_dir: bindir,
    install_mode: 'rwxr-xr-x',
    rename: 'rappit'
)

# 2. Install the application's source code and data files
install_subdir(
    'src',
    install_dir: app_datadir,
    exclude_directories: ['__pycache__'],
    strip_directory: true
)

# 3. Install GSettings schema
install_data(
    'src/data/io.github.fkkarakurt.rappit.gschema.xml',
    install_dir: datadir / 'glib-2.0/schemas'
)

# 4. Install Desktop Integration Files

# Desktop Entry
install_data(
    'src/data/io.github.fkkarakurt.rappit.desktop',
    install_dir: datadir / 'applications'
)

# AppStream Metainfo
install_data(
    'src/data/io.github.fkkarakurt.rappit.metainfo.xml',
    install_dir: datadir / 'metainfo'
)

# 5. Install Icons

# Hicolor icon directory
icon_dir = datadir / 'icons/hicolor'

# Scalable icon
install_data(
    'src/data/icons/hicolor/scalable/apps/io.github.fkkarakurt.rappit.svg',
    install_dir: icon_dir / 'scalable/apps'
)

# Symbolic icon
install_data(
    'src/data/icons/hicolor/symbolic/apps/io.github.fkkarakurt.rappit-symbolic.svg',
    install_dir: icon_dir / 'symbolic/apps'
)

# 6. Install UI files
install_data(
    'src/data/gtk/help-overlay.ui',
    install_dir: app_datadir / 'gtk'
)

# 7. Install bundled fonts (if any)
if run_command('test', '-d', 'fonts', check: false).returncode() == 0
    install_subdir(
        'fonts',
        install_dir: app_datadir
    )
endif

# --- Post-install script for GSettings schema ---
meson.add_install_script('post_install.py')

# --- Print installation summary ---
message('')
message('Rappit will be installed to:')
message('  Binary: ' + get_option('prefix') / bindir / 'rappit')
message('  Data: ' + pkgdatadir)
message('  Schemas: ' + get_option('prefix') / datadir / 'glib-2.0/schemas')
message('')
