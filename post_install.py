import os
import subprocess
import sys

def compile_schemas():
    schemas_dir = os.path.join(os.environ.get('MESON_INSTALL_PREFIX', '/app'), 'share/glib-2.0/schemas')

    if not os.path.exists(schemas_dir):
        return

    print('Compiling GSettings schemas...')
    try:
        subprocess.run(['glib-compile-schemas', schemas_dir], check=True)
        print('GSettings schemas compiled successfully')
    except subprocess.CalledProcessError as e:
        print(f'Error compiling schemas: {e}')
        sys.exit(1)

if __name__ == '__main__':
    compile_schemas()
