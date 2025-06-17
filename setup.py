from setuptools import setup, find_packages
import os

# Read README.md if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="kitsu_home_pipeline",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A toolkit for Kitsu pipeline integration with various DCC software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kitsu_home_studio",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "kitsu-task-manager=kitsu_home_pipeline.UI.task_manager.gui:run_gui",
        ],
    },
    package_data={
        "kitsu_home_pipeline": ["resources/*"],
    },
    include_package_data=True,
) 