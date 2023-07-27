from setuptools import find_packages  # , setup
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

setup(name="AsyncChatPractice",
      version="0.1.1",
      description="A Simple AsyncChatPractice Package",
      author="GB's student Nikita Bulatov",
      packages=find_packages(),
      author_email="nikita_bulatov@icloud.com",
      url="https://github.com/NikBulatov/AsyncChatPractice",
      options={
          "build_exe": build_exe_options
      },
      executables=[Executable("server.py"), Executable("client.py")]
      )
