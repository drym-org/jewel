from setuptools import setup

requirements = ['Pyro5', 'simple-term-menu', 'click', 'reedsolo']

test_requirements = [
    'pytest',
    'pytest-pudb',
    'pytest-sugar',
    'pytest-tldr',
    'tox',
    'tox-gh-actions',
    'coveralls',
]

dev_requirements = ['flake8', 'bump2version', 'sphinx', 'pre-commit', 'black']

setup_requirements = ['pytest-runner']

setup(
    name='jewel',
    version='0.0.0',
    description='Prototyping environment for P2P storage schemes.',
    author='ABE',
    author_email='abe@drym.org',
    url='https://github.com/countvajhula/jewel',
    include_package_data=True,
    packages=['jewel'],
    test_suite='tests',
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    extras_require={'dev': dev_requirements, 'test': test_requirements},
    entry_points={
        'console_scripts': [
            'jewel=jewel.jewel:main',
            'jewel-start-peer=jewel.peer:main',
            'jewel-start-server=jewel.fileserver:main',
        ]
    },
)
