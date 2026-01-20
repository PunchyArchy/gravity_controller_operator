from setuptools import setup, find_packages

setup(
    name="gravity_controller_operator",
    version="2.2.5",
    description="SDK предоставляющий универсальный интерфейс для работы со многими промышленными контроллерами ввода-вывода (количество расширяемо)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="PunchyArchy",
    author_email="ksmdrmvscthny@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "pyModbusTCP",
        "pymodbus==3.6.9",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
