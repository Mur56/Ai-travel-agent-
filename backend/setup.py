"""
AI Travel Planner Backend Package

A professional AI-powered travel planning API built with FastAPI and LangGraph.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AI Travel Planner Backend"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="ai-travel-planner-backend",
    version="1.0.0",
    author="AI Travel Planner Team",
    author_email="support@aitravelplanner.com",
    description="Professional AI-powered travel planning API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/ai-travel-planner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-travel-planner=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "travel",
        "ai",
        "planning",
        "fastapi",
        "langchain",
        "langgraph",
        "api",
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-org/ai-travel-planner/issues",
        "Source": "https://github.com/your-org/ai-travel-planner",
        "Documentation": "https://github.com/your-org/ai-travel-planner/docs",
    },
)