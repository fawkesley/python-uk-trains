from setuptools import setup, find_packages

long_desc = """
Search for UK stations and train times.
"""
# See https://pypi.python.org/pypi?%3Aaction=list_classifiers for classifiers

setup(
    name='uktrains',
    version='0.0.4',
    description="Search for UK stations and train times.",
    long_description=long_desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ],
    keywords='trains,national rail',
    author='Paul M Furley',
    author_email='paul@paulfurley.com',
    url='http://paulfurley.com',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'requests',
        'requests_cache',
        'mock',
        'lxml'
    ],
    tests_require=[],
)
