# Changelog

## [1.0.0] - 2024-02-29
### Added
- Added versioning and branching strategy in the README.md. #5272
- Added support for Python 3.10 and SpinnakerSDK >= 3.0.0.68. #8166 (, #7663)
    - Compatible with spinnaker-python for Py3.10.
- Added an optional dependency to allow JLink usage. #4054
- Added multimeters. #7580
    - Added general multimeter class.
    - Added general Multicomp class (only MP730889 support so far). #7580
- Added icon to GUI. #8337

### Changed
- Updated Config workflow. #7426
    - Added possibility to use more than one project when loading config.
    - Added possibility to ignore 'needed' in tests to be executed.
    - Added possibility to input a config as a dict when initializing Resources.
    - Moved raw access to loaded config to a `raw_config` variable.
    - Changed default access to loaded config via `config` variable to only the prescribed project.
- Updated documentation. #3785, #5272, #6816, #8337
    - Added and rephrased information.
    - Removed versions older than 0.0.13 from documentation history.
    - Added logo and favicon.
- Updated searching for resources. # 3966
    - Should improve some of the "default" behaviors.
- Cleaned-up code style. #8354
- Added option to bypass user input on manual power supply and manual switch.

### Fixed
- Fixed a bug in Config.merge_configs() - the program crashed when there was an empty project in a config file. #7426
- Fixed installation line in docs - replaced `--extra-index-url` with `--index-url` (this should prevent unwanted packages with the same name).

## [0.0.16.post0] - 2023-01-30
### Fixed
- Fixed NXP MCULink writing. #6816, 6672

## [0.0.16] - 2023-01-06
### Added
- Added NXP MCULink support. #6319, #6652

### Changed
- Updated documentation. #5272

### Fixed
- Fixed usage of subprocess.

## [0.0.15.post1] - 2022-08-19
### Added
- Added possibility to erase external memory. #6185

## [0.0.15.post0] - 2022-05-26
### Fixed
- Fixed logging interference of method `find_available_resource`

## [0.0.15] - 2022-05-19
### Fixed
- Fixed exception handling in `prepare_tests` method. #5823
- Fixed `hidapi` freeze possibility. #5840
    - Added explicit timeout usage to `hidapi`.
- Fixed video recording infinity possibility. #5855
    - Set video recording thread to daemon.
- Fixed serial communicable fail if `vid` or `pid` is `None`.
- Fixed missing resources in setUp. #5875
    - Bug introduced in version 0.0.14.

### Added
- Added possibility to use resources in `setUpClass` and `tearDownClass`. #5824
- Added warning against usage of version 0.0.14.
- Added missing reference to Basler cameras in the docs. #5272

### Changed
- Updated `find_available_resource` method. #5823

## [0.0.14] - 2022-04-12

- Warning: Usage of this version is highly discouraged. This version of Brest was unfortunately plagued with bugs.

### Fixed
- Fixed versioned docs prerequisite.

### Added
- Added support for recursive test preparation. #5364
- Added GUI for device probing. #2850
- Added support for Basler cameras. #5180
- Added support for camera opencv API control. #5628

### Changed
- Changed versioned documentation config.
    - Automatic building of versioned docs including the current branch (not only tags).

## [0.0.13] - 2021-11-18

### Fixed
- Fixed variable deletion causing attribute error in cameras. #5079
- Fixed _frame_grabber log_args in exception (cameras). #4021
- Fixed the config merging upon resource searching to match config merging upon resource construction. #5258

### Added
- Added review/staging for documentation. #4586
- Added support for YKUSH Yepkit switchable usb hub (`brest.switches.YepkitSwitch`). #3645

### Changed
- Changed documentation template, added versioning capability. #3465

## [0.0.12] - 2021-03-19

### Fixed
- Fixed ST-Link read / write. #4058
- Fixed Python version requirement to allow for any Python 3.9.* version. #3879

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
- `InterfaceCommunicable` to `FrameCommunicationInterface`.
  `InterfaceCommunicable` is marked as deprecated and will be removed in the future.

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
