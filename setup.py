from setuptools import setup, find_packages

setup(
    name='blocktrail-python',
    version='1.0',
    description="BlockTrail's Developer Friendly API binding for Python",
    long_description='This package allows interacting with the BlockTrail API',
    maintainer='Ruben de Vries',
    maintainer_email='ruben@blocktrail.com',
    url='https://www.blocktrail.com/api/docs',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License'
    ],
    packages=find_packages("src"),
    package_dir={'': 'src'},
    install_requires=[
        'httpsig >= 1.1.0',
        'pycrypto >= 2.6.1',
        'requests >= 2.4.3',
    ],
)