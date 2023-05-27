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

If you found a bug or if you have any idea for the project feel free to open a new issue on github ! And if you want to directly contribute, you are welcome.

List of ressources that can be helpful when starting with the solidworks API:
- [Solidworks API](https://help.solidworks.com/2022/french/SolidWorks/sldworks/c_solidworks_api.htm?verRedirect=1)
- [Python examples](https://mycad.visiativ.com/sites/default/files/questions/answer/15/11/2019/solidworks_python_api.pdf)

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


### Ready-dxf
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

### Copy-full-assembly
This tool help you when copying multiple file or assembly. It will help you by updating path reference to new path reference:
- In the equation manager
#### How to use
```
pyswtools copy-full-assembly PATH_TO_DIR SRC_REPLACE TARGET_REPLACE
```
- `PATH_TO_DIR` is the path to directory with all the files to update
- `SRC_REPLACE` is the string in the current path reference that you want to replace (probably the name of the old directory)
- `TARGET_REPLACE` is the string in the current path reference that you want to replace (probably the name of the new directory)

### Auto-export

This tool help you export a directory (or a part) to other file extensions. The current exrports are:
- DXF
- STL
- Auto

The Auto mode will use the name of the part and see if an extension is specified in it (e.g. `DXF_my_part.SLDPRT`)

The DXF export will only work when there is only one body in the part. Also the face that will be exported is a planar one with the biggest surface.

The STL export will consider the z axis as being the vertical dimension.

#### How to use


```
pyswtools auto-export PATH/TO/DIR MODE
```

With `Mode` being `AUTO`, `DXF` or `STL`. It will create directory with the extension used  and the corresponding files in it.

### Stat
This tool help you get stat on an assembly. It can gives you recursive information about the mass of each component of an assembly.

#### How to use

```
pyswtools stat PATH/TO/ASSEMBLY OPTIONS
```

You can select the display mode:
- `--tree`: (default) It will follow the structure from the assembly file
- `--list`: It will output to a single list

You can select the sort:
- `--mass`: (default) sort with a decreasing mass
- `--name`: sort with alphabetical order
