from setuptools import setup, find_packages

setup(
    name="nova-libvirt-exporter",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "prometheus-client>=0.16.0",
        "libvirt-python>=8.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "nova-libvirt-exporter=nova_libvirt_exporter.exporter:main",
        ],
    },
)
