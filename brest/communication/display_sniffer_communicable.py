import logging
import socket

from brest.communication import Communicable


class DisplaySnifferCommunicable(Communicable):
    """
    Class for representing USB as a resource.

    :param params: Construction params
    :type  params: dict
    """

    TYPE = "display_sniffer"
    TAKEN = []
    SETTINGS = []

    def __init__(self, params):
        self.log_args = {
            "class_name": self.__class__.__module__ + "." + self.__class__.__name__
        }
        self.logger = logging.getLogger()
        if params:
            self.address = params["address"]
            self.serial_number = params["serial_number"]
            self.mark_taken()

    def release(self):
        self.unmark_taken()

    def get_connections(self):

        from display_sniffer import list_fx3_devices

        generated_list = list_fx3_devices()
        sniffer_list = []
        for value in generated_list:
            one_fx3 = value.__dict__
            one_fx3["service"] = "sniffer_usb"
            sniffer_list.append(one_fx3)
        return sniffer_list

    def _list_connections(self):
        try:
            import display_sniffer

            return self.get_connections()
        except ModuleNotFoundError:
            return []

    def probe(self, interface, connections=None):
        def __device_to_interface(interface, device_id, index, connections):
            new_interface = dict(interface)
            new_interface["address"] = connections["address"]
            new_interface["index"] = index
            new_interface["serial_number"] = device_id
            return new_interface

        probed = []

        if not connections:
            connections = self._list_connections()

        for cam in connections:
            if interface["service"] == cam["service"]:
                if interface["serial_number"] is not None and str(interface["serial_number"]) != cam["serial_number"]:
                    continue

                probed.append(
                    __device_to_interface(
                        interface, cam["serial_number"], connections.index(cam) + 1, cam
                    )
                )

        return probed

    def mark_taken(self):
        self.TAKEN.append((self.__class__.__name__, self.address))

    def unmark_taken(self):
        try:
            self.TAKEN.remove((self.__class__.__name__, self.address))
        except ValueError:
            pass

    def is_taken(self, interface):
        for taken in DisplaySnifferCommunicable.TAKEN:
            if interface["address"] == taken[1]:
                return True
        return False

    def get_available(self, class_name, interface, connections):
        resources = []
        interfaces = self.probe(interface, connections)
        for interface_ in interfaces:
            if not self.is_taken(interface_):
                resources.append({"class_name": class_name, "interface": interface_})
        return resources

    def format_interface(self, interface):
        attrs = []
        # Called on constructed object
        if isinstance(interface, DisplaySnifferCommunicable):
            attrs.append(("type", interface.TYPE))
            attrs.append(("index", str(interface.index)))
            attrs.append(("service", interface.service))
        # Called on TAKEN record
        elif isinstance(interface, tuple):
            attrs.append(("class_name", interface[0]))
            attrs.append(("index", interface[1]))
            attrs.append(("service", interface[2]))
        # Called on interface dict
        elif isinstance(interface, dict):
            for name, value in interface.items():
                attrs.append((name, value))
        return attrs
