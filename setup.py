from setuptools import setup

setup(
    name='elastic_web_interface',
    packages=['elastic_web_interface'],
    include_package_data=True,
    install_requires=[
        'flask',
        'wtforms',
        'elasticsearch',
        'flask-paginate',
        'flask-bootstrap',
    ],
)
