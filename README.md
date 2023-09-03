# cpg_scpi

Educational client library to use Adafruit Circuit Playground (CPG) or BBC micro:bit via SCPI protocol in Python3.


## Description

The corresponding Arduino Sketch for the Circuit Playground can be found [here](https://github.com/GeorgBraun/SCPI-for-Adafruit-Circuit-Playground).

The corresponding MicroPython source code for the BBC micro:bit will be published in future.

... more docu to come ...





## Development

### Build pypi package

Tools needed to build and publish to PyPi under Windows:

```
python -m pip install --upgrade build
python -m pip install --upgrade twine
```

Tools needed to build and publish to PyPi Linux/MacOS:

```
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
```


Build package:

In project root folder:

```
python -m build
```

Upload package to pypi:

In project root folder:

```
twine upload --skip-existing dist/*
```

Alternatively, before uploading, delete outdated build artifacts in the `dist` folder, such that only the latest build files are uploaded:

```
twine upload dist/*
```


### Test pypi package

1. Create a test folder (e.g. `tests`) and cd into it.
1. Create virtual environment:
   * Windows: `python -m venv .venv`
   * Linux/MacOS: `python3 -m venv .venv`
1. Activate virtual environment:
   * Windows CMD: `.venv\Scripts\activate.bat`
   * Linux/MacOS: `source .venv/bin/activate`
1. Install package
   * Windows CMD: `pip3 install cpg-scpi`
   * Linux/MacOS: `pip3 install cpg-scpi`
   
