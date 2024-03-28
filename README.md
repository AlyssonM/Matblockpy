# MATLAB-Blockchain integration with Python (matpower case study)

This project integrates MATLAB with blockchain technology using Python, with a focus on power system simulations through MATPOWER as a case study. The project demonstrates how MATLAB can interact with Python to leverage blockchain functionalities, enhancing the capabilities of power system analysis and optimization.

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

 ## Installing matpower 7.1 (latest Release)
 MATPOWER is a package of free, open-source Matlab-language M-files for solving steady-state power system simulation and optimization problems, such as:

* power flow (PF),
* continuation power flow (CPF),
* extensible optimal power flow (OPF),
* unit commitment (UC) and
* stochastic, secure multi-interval OPF/UC.

To install it, get a copy by downloading and extracting the downloaded [ZIP file](https://matpower.org/about/get-started/). Or use git clone. <MATPOWER> denote the path to the directory:

```shell
    cd <MATPOWER>
    git clone https://github.com/MATPOWER/matpower.git
``` 
1. Open MATLAB or Octave and change to the <MATPOWER> directory.
2. Run the installer and follow the directions to add the required directories to your MATLAB or Octave path, by typing:

```shell
    install_matpower
``` 

If you chose not to have the installer run the test suite for you in step 2, you can run it now to verify that MATPOWER is installed and functioning properly, by typing:

```shell
    test_matpower
``` 

## Running MATPOWER 
To load the 30-bus system data from case30.m, increase its real power demand at bus 2 to 30 MW, then run an AC optimal power flow with default options, type:

```shell
    define_constants;
    mpc = loadcase('case30');
    mpc.bus(2, PD) = 30;
    runopf(mpc);
``` 
The MATPOWER documentation is available on the MATPOWER [website](https://matpower.org/doc/).
