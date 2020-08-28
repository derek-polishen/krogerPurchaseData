from setuptools import setup

setup(
    name="my-kroger-data",
    version="0.1",
    author="Derek Polishen",
    author_email="derek.polishen@gmail.com",
    description="Tool that allows a Kroger shopper to analyze previous transactions",
    url="https://github.com/derek-polishen/my-kroger-transactions",
    license="MIT",
    install_requires=['pandas', 'numpy', 'requests', 'seaborn', 'getpass','json','plotly', 'matplotlib','datetime', 'time'],
    zip_safe=False
)
