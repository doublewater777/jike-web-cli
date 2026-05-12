from setuptools import find_namespace_packages, setup

setup(
    name="cli-web-jike",
    version="0.1.1",
    description="CLI for Jike (即刻) — agent-native interface to web.okjike.com",
    packages=find_namespace_packages(include=["cli_web.*"]),
    package_data={"": ["skills/*.md", "*.md"]},
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "httpx>=0.24",
        "rich>=13.0",
        "prompt_toolkit>=3.0",
    ],
    extras_require={
        "auth": ["playwright>=1.30"],
    },
    entry_points={
        "console_scripts": [
            "cli-web-jike=cli_web.jike.jike_cli:main",
        ],
    },
)
