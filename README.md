# pySwTools

pySwTools is a combination of tools that I made to help me with my workflow when working with Solidworks. Sometimes it is not directly link to SW but more to what I do with the CAD models.

## Installation

You can directly install it from pypi:
```
pip install pySwTools
```

Or you can install it from this repository:
```
pip install .
```


## Contributing

If you found a bug or if you have any idea for the project feel free to open a new issue on github ! And if you want to directly contribute, you are welcome

## List of modules

### CLI
It is the main module of this project. It allows you to select the actions that you want to apply.

### Ready_DXF
Prepare dxf files from solidworks to be laser cutted:
- Remove the solidworks text from the output dxf file

#### How to use
You can use the following command:
```
pyswtools ready-dxf /path/to/file.dxf
```

It will output a `clean.dxf` file.

You can also provide the path to a directory with dxf inside

```
pyswtools ready-dxf /path/to/directory/
```

It will output a `directory_cleaned` directory with all the cleaned dxf.

#### Features to come
- [ ] Combine Lines
- [ ] Combine Files
- [ ] Add auto coloring
- [ ] Add tests

### Copy_full_assembly
- [ ] To migrate

### Exports_to_STL
- [ ] To migrate
### Exports_to_dxf
- [ ] To migrate
