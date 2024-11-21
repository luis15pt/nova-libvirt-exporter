from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nova-libvirt-exporter",
    version="0.1.0",
    author="Luis Sarabando",
    author_email="luis15pt@gmail.com",
    description="A Prometheus exporter for OpenStack Nova instances using libvirt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luis15pt/nova-libvirt-exporter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    install_requires=[
        "prometheus-client>=0.16.0",
        "libvirt-python>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "nova-libvirt-exporter=nova_libvirt_exporter.exporter:main",
        ],
    },
)
