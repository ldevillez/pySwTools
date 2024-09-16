# Changelog

## [Unreleased]
### Added
- Adding the type of component into the display of the stat module
- Adding a flag to filter the type of components
- Adding the number of drawings using the parts
### Changed
### Deprecated
### Removed
### Fixed
- Fixing an issue with the configuration name removal. Some parts were not correctly counted in the tree display.
### Security

## v0.7.1 - 2024/09/12
### Fixed
- Do not count suppressed components in the stat module
- Add condition to avoid crash on non readable masss properties

## v0.7.0 - 2023/06/19
### Added
- Adding density info to stat module
- Adding flag to stat module to get only elements with default density
- Adding clean module
- Adding function to get directly sw_app, sw_doc
- Adding bool function to test if file is assembly, part or temporary
- Adding sorting option to mass of the part
- Handling conf in the stat module
### Changed
- Improving the output of the state module with tabular like output
- Updating the doc in the README for the stat module
- Enum in click option for stat module
- Changing option flag to choice for stat module
### Deprecated
### Removed
### Fixed
- Fix typo in maintainer name
- Fix stat module for no volume part
### Security

## v0.6.0 - 2023/05/27
### Added
- Adding stat module
### Changed
### Deprecated
### Removed
### Fixed
- Correcting README
### Security

## v0.5.0 - 2023/05/04

### Added
- Adding auto_export module
### Changed
- Changing used version of pydantic
### Deprecated
### Removed
### Fixed
### Security

## v0.4.0 - 2023/05/04

### Added
- Adding copy full assembly
- Adding config handler
- Adding a utils folder for generic functions
### Changed
### Deprecated
### Removed
### Fixed
- Correct cli not executing the commands
### Security

## v0.3.0 - 2023/05/03

### Added
- Adding `pyproject.toml`
- Adding issue and PR template
- Adding formating (black) and linting (pylint) github action

### Changed
- Changing the project from Ready-dxf to a collection of tools

### Removed
- Removing `requirements.txt`


## v0.1 - 2022/05/15
### Added
- Installation instruction for Ready-dxf
- How to use instruction for Ready-dxf
- Folder handler for Ready-dxf

## v0.0 - 2022/05/10
### Added
- Proof of concept for Ready-dxf
