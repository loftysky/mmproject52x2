from setuptools import setup, find_packages

setup(
    name='mmproject52x2',
    version='0.1.dev0',
    description='Mark Media\'s Render Tools',
    url='',
    
    packages=find_packages(exclude=['build*', 'tests*']),
    include_package_data=True,
    
    author='Elaine Wong',
    author_email='elainew@loftysky.com',
    license='BSD-3',
    
    entry_points={
        'console_scripts': '''
            mm52x2-render-schedule = mmproject52x2.render.schedule:main
            mm52x2-premiere-install = mmproject52x2.premiere.install:main
        ''',
    },

    metatools_scripts={
        'mm52x2-render': {
            'entrypoint': 'mmproject52x2.render.core:main',
            'interpreter': 'mayapy',
        }
    },

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
)
