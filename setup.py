from setuptools import setup, find_packages

setup(
    name='mmproject52x2',
    version='0.1.dev0',
    description='Mark Media\'s Rneder Tools',
    url='',
    
    packages=find_packages(exclude=['build*', 'tests*']),
    include_package_data=True,
    
    author='Mike Boers',
    author_email='mmmaya@mikeboers.com',
    license='BSD-3',

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
)
