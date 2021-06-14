from setuptools import find_packages, setup

setup(
    name="kickerapp",
    version="1.0.0",
    description="Kicker app",
    platforms=["POSIX"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["aiohttp>=3.7,<3.8", "fastjsonschema"]
)
