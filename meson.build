# Project definition
project('rappit', 'python',
    version: '1.0',
    license: 'AGPL-3.0',
    meson_version: '>=0.50.0',
    default_options: [
        'python.install_env=auto',
    ]
)

# Configuration variables
app_id = 'io.github.fkkarakurt.rappit'
python = import('python').find_installation('python3')
gnome = import('gnome')

# Dependencies
pygobject_dep = dependency('pygobject-3.0', version: '>=3.42.0')
gtk4_dep = dependency('gtk4', version: '>=4.0.0')
libadwaita_dep = dependency('libadwaita-1', version: '>=1.0.0')
gtksource_dep = dependency('gtksourceview-5', version: '>=5.0.0')

# Installation directories
prefix = get_option('prefix')
bindir = prefix / get_option('bindir')
datadir = prefix / get_option('datadir')
pkgdatadir = datadir / app_id
schemadir = datadir / 'glib-2.0' / 'schemas'

# Install main executable
configure_file(
    input: 'run.py',
    output: 'rappit',
    copy: true,
    install: true,
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

# Install Python source code
install_subdir(
    'src',
    install_dir: pkgdatadir,
    exclude_directories: ['__pycache__'],
    strip_directory: true
)

# Install GSettings schema
install_data(
    'src/data/io.github.fkkarakurt.rappit.gschema.xml',
    install_dir: schemadir
)

# Compile GSettings schemas
gnome.compile_schemas()

# Desktop integration
install_data(
    'src/data/io.github.fkkarakurt.rappit.desktop',
    install_dir: datadir / 'applications'
)

install_data(
    'src/data/io.github.fkkarakurt.rappit.metainfo.xml',
    install_dir: datadir / 'metainfo'
)

# Icons
install_data(
    'src/data/icons/hicolor/scalable/apps/io.github.fkkarakurt.rappit.svg',
    install_dir: datadir / 'icons/hicolor/scalable/apps'
)

install_data(
    'src/data/icons/hicolor/symbolic/apps/io.github.fkkarakurt.rappit-symbolic.svg',
    install_dir: datadir / 'icons/hicolor/symbolic/apps'
)

# UI files
install_data(
    'src/data/gtk/help-overlay.ui',
    install_dir: pkgdatadir / 'gtk'
)

# Post-install script for schema compilation
meson.add_install_script('post_install.py')
