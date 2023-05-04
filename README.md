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

If you are on windows, maybe the directory where the script is installed will not be on the PATH but it can be added to directly be able to use the script from a command prompt.


## Contributing

If you found a bug or if you have any idea for the project feel free to open a new issue on github ! And if you want to directly contribute, you are welcome

## List of modules

### CLI
It is the main module of this project. It allows you to select the actions that you want to apply. To directly get help from the tool simply type:
```
pyswtools
```

### Config
This command helps you handling your config. By default, the config is the following:
```
sw_version: 2022 # This is important to set the correct version
```

If you want to modify the config, you need to first create a file with :
```
pyswtools config init
```

And you can reset to the default config with:
```
pyswtools config init --force
```

If you want to get the current config:
```
pyswtools config dump
```
Or the path to the current config:
```
pyswtools config dump --path
```


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
pyswtools ready-dxf /path/to/directory
```

It will output a `directory_cleaned` directory with all the cleaned dxf. Do not include the `/` or `\` at the end of the path of the directory

#### Features to come
- [ ] Combine Lines
- [ ] Combine Files
- [ ] Add auto coloring
- [ ] Add tests

### Copy_full_assembly
This tool help you when copying multiple file or assembly. It will help you by updating path reference to new path reference:
- In the equation manager
#### How to use
```
pyswtools copy-full-assembly PATH_TO_DIR SRC_REPLACE TARGET_REPLACE
```
- `PATH_TO_DIR` is the path to directory with all the files to update
- `SRC_REPLACE` is the string in the current path reference that you want to replace (probably the name of the old directory)
- `TARGET_REPLACE` is the string in the current path reference that you want to replace (probably the name of the new directory)

### Exports_to_STL
- [ ] To migrate
### Exports_to_dxf
- [ ] To migrate
