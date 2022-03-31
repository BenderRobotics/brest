from brest import ResourceProvider

import logging
class ResourceModel:

    # List of converter's attributes
    # This is temporary until new Brest architecture
    # Don't judge me
    conv = [
        {
            'name': 'FTDI_UART',
            'vid': 0x0403,
            'pid': 0x6015
        },
        {
            'name': 'FTDI_RS232',
            'vid': 0x0403,
            'pid': 0x6001
        },
        {
            'name': 'CP210x',
            'vid': 0x10C4,
            'pid': 0xEA60
        },
        {
            'name': 'PL2303 Serial Port',
            'vid': 0x067B,
            'pid': 0x2303
        },
        {
            'name': 'HL-340 USB-Serial adapter',
            'vid': 0x1A86,
            'pid': 0x7523
        },
    ]

    def __init__(self):
        self.log_args = {'class_name': self.__class__.__name__}
        self.logger = logging.getLogger('brest')

        self.resource_provider = ResourceProvider()
        self.resources = []

    def get_connected_devices(self):
        try:
            # If ResourceProvider.available() is called from other thread
            # than object was created, listing camera fails
            # Get available devices
            self.resources = []
            resources = self.resource_provider.available()

            for resource in resources:
                resource_object = self.resource_provider._get_communicable(resource['interface']['type'])
                resource['interface'].update(resource_object.format_interface(resource['interface']))

                # Handle name translation for known USB <-> serial converters
                if 'serial' == resource['interface']['type']:
                    known_converter = [d for d in self.conv if (d['vid'], d['pid']) == (resource['interface']['vid'], resource['interface']['pid'])]
                    if known_converter:
                        resource['interface'].update({'name':known_converter[0]['name']})

                self.resources.append(resource)

        except Exception as ex:
            self.logger.error(str(ex), extra=self.log_args)
        finally:
            return self.resources
