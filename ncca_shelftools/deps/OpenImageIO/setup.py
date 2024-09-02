from setuptools import setup
from setuptools.command.build_ext import build_ext as build_ext_orig
import os
import sys

class build_ext(build_ext_orig):
    def build_extensions(self):
        # Determine the correct shared object extension based on platform
        if sys.platform == 'win32':
            ext = 'dll'
        elif sys.platform == 'darwin':
            ext = 'dylib'
        else:
            ext = 'so'

        # Ensure the shared object file is in the right location
        shared_lib = f'OpenImageIO.{ext}'
        lib_path = os.path.join(self.build_lib, 'OpenImageIO', shared_lib)
        if not os.path.exists(lib_path):
            os.makedirs(os.path.join(self.build_lib, 'OpenImageIO'), exist_ok=True)
            # For simplicity, let's assume it's already in the right location
        super().build_extensions()

setup(
    name='OpenImageIO',
    version='2.6.4',
    packages=['OpenImageIO'],
    package_dir={'': '.'},
    package_data={
        'OpenImageIO': [
            'OpenImageIO.cpython-39-x86_64-linux-gnu.so',
            'OpenImageIO.pyd',  # This is for Windows .pyd files
            'OpenImageIO.dylib'  # This is for macOS .dylib files
        ],
    },
    install_requires=[
        # List your dependencies here
    ],
    cmdclass={'build_ext': build_ext},
    description='A Python package for OpenImageIO. Designed by the NCCA Labs at Bournemouth University',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AcademySoftwareFoundation/OpenImageIO/tree/master',  # Replace with your URL
    author='Christopher Hosken',
    author_email='hoskenchristopher@gmail.com',
)
