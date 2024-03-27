# MATLAB-Blockchain integration with Python (matpower case study)

## Requirements

The Python versions used must be compatible with your [MATLAB Product](https://www.mathworks.com/support/requirements/python-compatibility.html).
The examples in this repository utilize MATLAB R2020b and Python 3.11.

## Create Virtual Env 

```shell
    cd <path>
    python -m venv <venvname>
```

## Configure MATLAB to use Python Virtual Env

After MATLAB startup on Windows, to set the version type:
```shell
    pyenv("Version","<venv-path>\Scripts\python.exe")
```
For macOS and Linux:
```shell
    pyenv(Version="<venv-path>/bin/python3.11")
```

## Import python modules in .m scripts
To import Python modules, use the following code:
```shell
    clear classes     % used to reload python modules updates (also clean entire workspace)
    mod = py.importlib.import_module('yourmodule');
    py.importlib.reload(mod);  % force modure reload to updates changes
```

## Acessing functions in python modules
To call Python functions from MATLAB, use the following syntax:
```shell
    r = py.yourmodule.func(listOfParams)
``` 
 _'r'_ represents a variable to receive returns and can be any variable name; it will be loaded into the MATLAB workspace. _'listofParams'_ can be null with an empty call _func()_, or the respective sequence, _func(param1, param2, ..., paramN)_.