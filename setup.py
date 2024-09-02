from setuptools import setup, find_packages

classifiers = [
	"Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS :: MacOS X",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3"
]

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flask-neon-kit",
    version="0.0.3",
    description="Automatically generates Flask CRUD endpoints from defined Neon Postgres models",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="",
    author="Valentine Sean Chanengeta",
    author_email="seanchanengeta@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords=[
        "neon-oss-starter-kit",
        "flask-neon-kit",
        "flask-crud",
	],
    packages=find_packages(),
    install_requires=[
        "alembic==1.13.2",
        "blinker==1.8.2",
        "click==8.1.7",
        "colorama==0.4.6",
        "Flask==3.0.3",
        "Flask-Migrate==4.0.7",
        "Flask-SQLAlchemy==3.1.1",
        "greenlet==3.0.3",
        "itsdangerous==2.2.0",
        "Jinja2==3.1.4",
        "Mako==1.3.5",
        "MarkupSafe==2.1.5",
        "psycopg2==2.9.9",
        "SQLAlchemy==2.0.32",
        "typing_extensions==4.12.2",
        "Werkzeug==3.0.4",
	]
)