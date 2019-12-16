# Changelog

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
