# Changelog

## [0.0.12] - 2021-03-19

### Fixed
- Fixed ST-Link read / write. #4058
- Fixed Python version requirement to allow for any Python 3.9.* version. (refs #3879)

### Changed
- Improved camera color calibration procedure. #4188

## [0.0.11] - 2020-12-14

### Fixed
- Fixed log formatting propagation that caused problems on Python 3.9. #3802
- Fixed Cleware Serial Number reading upon probing. #3767
- Fixed operator in one of the modules. #3812

### Changed
- Changed Python version check. #3802
    - Can be installed on Python 3.5 - 3.9.
    - Importing on Python 3.8 - 3.9 gives warning on unproven support.
    - Importing on Python version other than (3.5 - 3.9) exits execution with error message.
- Changed timeout for Cleware Serial Number reading upon probing. #3767

## [0.0.10] - 2020-11-11

### Fixed
- Fixed serial_number parameter to be enough for SerialInterface. #3286
- Fixed IO parameters in 'definitions.rst'. #3707

### Added
- Added `USB-RLY02` to `brest.io.USBRelay`. #3707
- Added support for video acquisition using `brest.cameras`. #2409

### Changed
- Added fallback device for `brest.io.USBRelay` in case of unrecognized model. #3707
- Updated and added headers to files.
- From now on the module version will change only when there is a change in the module.
   In such case the version should match the corresponding Brest release version.

## [0.0.9] - 2020-05-26

### Fixed
- Fixed ST-Link timeout during connect operation. #3271

### Added
- Justified why ST-Link fails when it fails. #2639
- Initial multipath support for flasher devices. #3191
- `Manio` manual IO device. #3285

## [0.0.8] - 2020-05-15

### Added
- `brest.find_available_resource` tool method for finding resources without instantiation #3189
- Use case scenario for getting pyserial Serial object using Brest #3189
- `fill_t` and `bit_uint_t` packable types for messages
- Tenma model 72-2705 model support

### Changed
- Tenma model fallback in case of unrecognized model.

## [0.0.7] - 2020-04-03

### Fixed
- Serial numbers that contains dash will no longer be truncated #2786
- Subprocess don't close_fds on Windows #2648
- Deepcopy fails on Python 3.6.X #2853

### Added
- `brest.communication.modbus` module for all Modbus related stuff
- `ModbusInterface` for general Modbus use #2614
- Modbus `definitions` and `messages` #2614
- `SerialInterface` for representing a com port as a resource #2834
- `enum_t` to pack enums into messages #3041

### Changed
- `InterfaceCommunicable` to `FrameCommunicationInterface`. `InterfaceCommunicable` is marked
   as deprecated and will be removed in the future

## [0.0.6] - 2020-01-27

### Added
- `model` option for Tenma supplies in configuration file. #2771
- `status` property pro Tenma supplies. #2777

### Changed
- `Resource` class now fully behaves as a dict. #2676

## [0.0.5] - 2019-12-16

### Added
- `sn_timeout` option under `interface` group for Cleware devices. #2669

## [0.0.4] - 2019-12-16

### Changed
- Improved Cleware USB switch serial number detection. #2622
- Changed exception catched return value to `sys.exit(1)`.

## [0.0.3] - 2019-12-02

### Added
- Brest installation and updating using `pip`.
- Cycle function for supplies.
- Default protection setting for supplies in the configuration file.
- PointGrey camera default settings in the configuration file.
- Cleware USB switch support.
- Manually operable switch using prompts.
- Possibility to bypass resource disabling upon destruction.
- Generate configure file from available resources.
- `CLICommunicable` base class for communication with a cli utility.
- `HIDCommunicable` for communication with HID.

### Changed
- Camera support refactored.
- `Backfly` camera renamed to `PointGrey`.
- Resource instantiation logs now include project name

### Fixed
- Error during taken resources checking. #2547
- Reference loss on assignment to propagated channel. #2593
- Documentation mismatches. #2576
- Fixed error when prepare_tests() stumble upon failed test because of syntax error #2608

## [0.0.2] - 2019-11-04

### Added
- Manually operable supply using prompts.
- USB-RLY modules support.
- ST-Link flasher support.
- J-Ling flasher support.
- Project specific configuration that merges with user specific configuration file.

### Changed
- Available, taken and all resources printing.
- Configuration file syntax.
- Configuration file instantiation.
