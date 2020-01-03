from setuptools import setup


def get_readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="hawc",
    version="1.0.0",
    description="A content management system for human health assessments.",
    long_description=get_readme(),
    url="https://github.com/shapiromatron/hawc",
    author="Andy Shapiro",
    author_email="shapiromatron@gmail.com",
    license="MIT",
    packages=("hawc", ),
    entry_points={'console_scripts': [
        'manage.py = hawc:manage',
    ]},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
