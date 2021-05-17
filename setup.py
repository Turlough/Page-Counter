########################################
# 	python setup.py build
########################################

from cx_Freeze import setup, Executable
import distutils
import opcode
import os

distutils_path = os.path.join(os.path.dirname(opcode.__file__), 'distutils')

# includes = ["distutils", "PyPDF2", "PIL"]
build_exe_options = {
    "build_exe": 'build'
}

setup(name="Page Counter",
      version="2.0",
      description="Counts number of image-type pages in a directory",
      options={"build_exe": build_exe_options},
      executables=[Executable("page_counter.py")]
      )
