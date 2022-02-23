from setuptools import setup
setup(
    name='deb-builder',
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'deb-builder=debbuilder:main'
        ]
    }
)
