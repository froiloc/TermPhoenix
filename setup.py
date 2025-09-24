from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="termphoenix",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A intelligent web crawler that extracts special-interest terminology from websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/froiloc/TermPhoenix",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "termphoenix=termphoenix.main:main",
        ],
    },
)
