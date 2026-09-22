from setuptools import setup, find_packages

setup(
    name="coding_lms",
    version="0.0.1",
    description="Standalone Coding LMS Extension with Judge0 & Proctored Labs",
    author="Coding LMS",
    author_email="dev@codinglms.local",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "requests>=2.28.0"
    ]
)
