"""
Setup configuration for ipv6-only tools.
"""

from setuptools import setup, find_packages
import os


def read_file(filename):
    """Read file contents."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


setup(
    name='ipv6-only',
    version='0.1.0',
    description='Comprehensive IPv6-only networking tools and utilities',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='IPv6-Only Project',
    author_email='',
    url='https://github.com/Hyperpolymath/ipv6-only',
    packages=find_packages(where='src/python'),
    package_dir={'': 'src/python'},
    python_requires='>=3.7',
    install_requires=[
        # No external dependencies - uses only Python stdlib
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.990',
        ],
        'dns': [
            'dnspython>=2.0.0',
        ],
        'cli': [
            'click>=8.0.0',
            'rich>=12.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'ipv6-calc=ipv6tools.cli:calc_cli',
            'ipv6-validate=ipv6tools.cli:validate_cli',
            'ipv6-gen=ipv6tools.cli:generate_cli',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ],
    keywords='ipv6 networking subnet calculator validation',
)
