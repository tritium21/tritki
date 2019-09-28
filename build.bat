rmdir /q /s dist
if not exist "%~dp0build_env\" py -3.7 -m venv build_env
build_env\scripts\python -m pip install --upgrade pip wheel setuptools
build_env\scripts\python -m pip install --upgrade -r requirements_build.txt
build_env\scripts\pyinstaller run_tritki.spec
