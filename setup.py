from distutils.core import setup

setup(
    name='python-ramzinex',  # How you named your package folder (MyLib)
    packages=['ramzinex'],  # Chose the same as "name"
    version='0.9',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='Ramzinex Exchange API python implementation for automated trading',
    # Give a short description about your library
    author='Hossein',  # Type in your name
    author_email='hsnkhaki@gmail.com',  # Type in your E-Mail
    url='https://github.com/hsnkhaki',  # Provide either the link to your github or to your website
    download_url='https://github.com/hsnkhaki/python-ramzinex/archive/refs/tags/0.9.tar.gz',  # I explain this later on
    keywords=['trade', 'bitcoin', 'automate'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.6',
    ],
)

# To upgrade:
# change the version and download_url
# After change:
# python setup.py sdist
# twine upload dist/*
