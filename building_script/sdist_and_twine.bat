@echo off

set pyprojects_root="C:\Users\Andrew\Desktop\Pycharm_Projects\"
set project_full_path="%pyprojects_root%\SSHClientAJM"
REM this might be able to check python version FOR the user
set python_version=python -c "import platform;print(''.join(platform.python_version().split('.')[:-1]))"


cd %project_full_path%
echo pwd changed to %cd%

REM need LICENSE.txt README.md setup.cfg setup.py - see https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56
REM DONT FORGET TO UPDATE setup.py, push commit to remote, and create a new release!! THEN run this!!!
echo running dist setup

REM THIS IS THE COMMAND FOR PYTHON 3.10? and before.
REM python setup.py sdist

REM THIS IS THE COMMAND FOR PYTHON 3.12 and AFTER
python -m build

REM You can upload your distributions to TestPyPI using twine by specifying the --repository flag:
REM twine upload --repository testpypi dist/*
echo running twine to update pypi - token username is __token__
twine upload dist/*

REM You can tell pip to download packages from TestPyPI instead of PyPI by specifying the --index-url flag:
REM py -m pip install --index-url https://test.pypi.org/simple/ your-package
