# pySwTools

pySwTools is a combination of tools that I made to help me with my workflow when working with Solidworks. Sometimes it is not directly link to SW but more to what I do with the CAD models.

## Installation
- [ ] Add pyproject.toml
- [ ] Add instruction
## Contributing

If you found a bug or if you have any idea for the project feel free to open a new issue on github ! And if you want to directly contribute, you are welcome 

## List of modules

### CLI
- [ ] To do
- [ ] Add possibility for config (e.g. SW version to use)
- [ ] Add possibility to chain actions (e.g. export dxf, ready dxf)
### Ready_DXF
- [ ] To migrate
- [ ] Unit Lines
- [ ] Unit Files
- [ ] Add auto coloring
- [ ] Add tests

Prepare dxf files from solidworks to be laser cutted:
- Remove the solidworks text from the output dxf file

#### How to use
The only arguments of the tool is the path to the dxf file:
```
python main.py /path/to/file.dxf
```

It will output a `clean.dxf` file.

You can also provie the path to a directory with dxf inside

```
python main.py /path/to/directory/
```

It will output a `directory_cleaned` directory with all the cleaned dxf.


### Copy_full_assembly
- [ ] To migrate

### Exports_to_STL
- [ ] To migrate
### Exports_to_dxf
- [ ] To migrate






### 




## How to use


## Installation

The first step is to install the dependencies in requirements.txt:
```
pip install requirements.txt
```

Idealy it should be done in a [virtual env](https://docs.python.org/3/library/venv.html).

## What it does:
- Remove the solidworks text from the output dxf file

## Versions

### V0.2
- [ ] System Installation (Windows/Linux)


### V0.1
- [x] Installation instruction
- [x] How to use
- [x] Prepare folder of dxf

### V0.0
- [x] Proof of concepts
