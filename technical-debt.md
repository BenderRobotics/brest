# Technical Debt

## Inheritance of interfaces
Inheritance is the strongest form of coupling and imposing depedency. In context of the resources and corresponding interfaces for communication, it makes them tightly tied together. Rather than being able to use a unified API for the interface.

>For example, if a new version of the hardware uses a different protocol (e.g., HID or Modbus), the entire inheritance tree must be duplicated or refactored. A compositional approach would be much cleaner.

The solution is dependency injection, where the interface would be instantiated separately and it would be passed as a constructor parameter to the given resource. This would also solve the issue of the pool, since the pool would be managing the interfaces, not the resources.

## Testing limitations
This issue is a direct consequence of the previous section. Given the strictly inherited relationship between a resource and a given interface, the interface must be heavily mocked.

```python
scenario_serial=FakeCom(port="COM999", vid=0x0416, pid=0x5011, serial="SN999")

with patch('serial.Serial') as mock_serial_class, \
    patch('brest.pyserial_tools.list_ports.comports') as mock_comports, \
    patch.object(SerialCommunicable, 'get_connections') as mock_conn, \
    patch.object(SerialCommunicable, 'probe') as mock_probe, \
    patch.object(SCPICommunicable, 'write_raw') as mock_write, \
    patch.object(SCPICommunicable, 'read_raw') as mock_read:

    mock_conn.return_value = [scenario_serial]
    mock_comports.return_value = [scenario_serial]

    mock_serial_instance = mock_serial_class.return_value
    mock_serial_instance.port = scenario_serial.port
    mock_serial_instance.isOpen.return_value = False
```

If we were to use dependency injection and a unified API for the interfaces, it would be much easier, since we could replace the object altogether and just implemented the methods as described by the API.

## Inconsistent exception handling
>Setting values out of bounds is ignored and logged, an exception is preferred.

A unified approach isn't adopted in the codebase to handle such situations. Exception handling should be used and the subsequent handling could be used to notify the user.

## Undefined API
The abstract multimeter base class doesn't define the API/methods which the Multicomp child class should implement. These definitions are especially useful if we're adding other classes and it would clarify the module structure as a whole.

## Properties of resource cannot be defined within config
Suppose some models are able to perform temperature measurements, while others are not.  In such cases, it would be useful to able to describe the temperature measurement capability for a multimeter  within the config.

Though the config is very useful in case of general requirements for a multimeter, it doesn't sufficient granularity to distinguish between certain models in classes, such as `Multimeters.Multicomp`.

## print_* methods semantics
Given the resource discovery methodology of choice, the brest API methods do not provide exact information about the resources.

Below is a snippet of the `print_available()` method's output:

```yaml
[1] supplies.MP71 | multimeters.Multicomp | multimeters.MP71 | multimeters.MP73
    type: serial
    timeout: 0.1
    vid: 0x1A86
    pid: 0x7523
    baudrate: 115200
    serial_number: 6&113C82D5&0&2
    port: COM10
```

Given there are several resources which can be identified with the same `vid`, `pid` combination, it is not possible to determine without further probing the interface. This information is currently compared to the `KNOWN` property of the resource classes.

## Base classes don't contain common behavior
Sometimes, there is a lack of shared functionality within the base class, even though it could be included there. This introduces some redundant duplicates in the code.

## Weird naming conventions in Public API
`Mansup`, now added `Manmulti`.

## Accounting for user error in manual resources
Regarding `Man*` classes, the user error isn't accounted for. For example, if the user enters an invalid value, it is currently ignored and logged. However, it would be better to ask the user again.

```python
 if not self._BYPASS_USER:
    val_str = input(
            '{}: Read {} from the multimeter in {} and enter the value: '
            ''.format(self.name, measurement_type, unit_str)
    )
    try:
        return float(val_str)
    except ValueError:
        self.logger.error('{}: Invalid value entered. Returning 0.0'.format(self.name), extra=self.log_args)
        return 0.0
 else:
    self.logger.warning('{}: Bypassing user input as given by config. Returning 0.0'.format(self.name), extra=self.log_args)
    return 0.0
```

## Lack of type hints
The codebase lacks type hints, which makes it harder to understand the code and to find potential bugs.

## Overcomplicated API
The current API relies on distinct methods for each measurement type (e.g., `measure_voltage()`, `measure_current()`), which may be unnecessarily verbose.

A unified `measure(unit)` approach could deduce the measurement type directly from the requested unit, significantly simplifying the interface.

Furthermore, the current architecture ties capabilities strictly to physical hardware forms (e.g., assuming all measurements come from a `Multimeter`). This decomposition becomes restrictive for specialized instruments like dedicated RCL meters, highlighting a need to decouple hardware form factors from their underlying measuring capabilities.

## Focusing on REPL readability instead of returning API-friendly objects.
Instead of returning structured, typed objects (e.g., a `dataclass`) that can be seamlessly evaluated in programmatic logic, methods like the one above return highly formatted strings nested within arbitrary dictionary keys.

```python
def get_info(self):
    device_info = self.transceive(self.Commands.GET_INFO).replace(',', ', ').strip('\r\n')
    mode_val = self.transceive(self.Commands.GET_MODE).strip('\r\n')
    response = {"Device information": device_info, "Status": mode_val}
```

## Multi-channel resources

The resource abstraction is not ideal to achieve full potential of brest. The users should be able to specify they want a channel from a PSU rather than having to manually look for a PSU which has multichannel capabilities.

## GET_STATUS

The currently implemented `get_status()` in Tenma is not easily transferable across resources. (i.e. supplies.Tenma -> supplies.MP71)
Though it is possible to achieve similar behavior in different supplies, the commands and returned values from each supply may be different.

## Inconsitent resource identification

The logic in `print_available()` creates indexes for resources on the fly. These indexes are directly used in the `construct_available(index)` method. This could lead to unexpected behaviour for the users, as these indexes are not persistent and change across multiple runs with disconnects and resource constructions between the respective calls.

It would be better if the resource indexes were consistent across the whole session. Therefore, should any changes occur between calls, the indexes of the resources listed would remain the same.

The implementation would require keeping tracks of all available/taken resources across the session and generating consistent indexes for each of the resources.

## Using @property for I/O bound operations
The property call is somewhat hidden to the user, on a first glance it seems it is just a member access without additional cost.
Having I/O operations (sending request to device) in property can be confusing for the user, as he might not expect getting transmition exceptions or transmition delays on a simple access.
