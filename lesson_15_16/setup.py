from setuptools import find_packages  # , setup
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}
with open("../requirements.txt", "r", encoding="utf-8") as req:
    REQUIREMENTS = [line.split("==")[0] for line in req.readlines()]

setup(name="AsyncChatPractice",
      version="0.1.3",
      description="A Simple AsyncChatPractice Package",
      author="GB's student Nikita Bulatov",
      packages=find_packages(),
      author_email="nikita_bulatov@icloud.com",
      url="https://github.com/NikBulatov/AsyncChatPractice",
      install_requires=REQUIREMENTS,
      options={
          "build_exe": build_exe_options
      },
      executables=[Executable("server.py"), Executable("client.py")]
      )
