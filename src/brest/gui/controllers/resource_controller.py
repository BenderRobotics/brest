from brest.gui.views import ResourceView
from brest.gui.models import ResourceModel

import time
import queue
import logging
import threading


class ResourceController:

    def __init__(self, master):
        self.log_args = {'class_name': '{}'.format(self.__class__.__name__)}
        self.logger = logging.getLogger('brest')

        #: Wait time between checking currently connected devices
        self.REFRESH_RATE = 1
        #: Wait time between draw checking on connected devices treeview
        self.REDRAW_RATE = 250
        #: Indicates if devices refresh should be done
        self.refresh = True

        self.master = master
        # self.resource_model = ResourceModel()
        self.resource_view = ResourceView(master)

        self._hashes = []
        #: Queue to pass connected devices between threads
        self._connected_devices = queue.Queue()
        #: Indicates if queue is being filled to prevent
        self._is_filling = False

        #: Thread for device refreshing
        self.refresh_thread = threading.Thread(target=self.__refresh_loop, daemon=True)
        self.refresh_thread.start()

        self.master.after(self.REDRAW_RATE, self.redraw_devices)

    def add_resource(self):
        pass

    def del_resource(self):
        pass

    def redraw_devices(self):
        """
        Check queue of connected devices and redraw changes
        """

        # Check if data was fetched of if queue is being filled now
        if self._connected_devices.qsize() == 0 or self._is_filling:
            self.master.after(self.REDRAW_RATE, self.redraw_devices)
            return

        # Empty queue to list
        connected_devices = []
        try:
            while True:
                device = self._connected_devices.get(block=False)
                connected_devices.append(device)
        except queue.Empty:
            pass

        # Clear the tree view
        for resource in self._hashes:
            if (resource['hash'] not in connected_devices):
                self.resource_view.tree.delete(resource['item'])
                self._hashes.remove(resource)

        # Iterate through connected device and add them to the tree view
        for resource in connected_devices:
            if resource not in [r['hash'] for r in self._hashes]:
                t_res = self.resource_view.tree.insert("", "end", text=resource['class_name'], values=[""], open=True)
                for int_attr_name, int_attr_value in resource['interface'].items():
                    val = int_attr_value if int_attr_value is not None else "none"
                    added = self.resource_view.tree.insert(t_res, "end", text=int_attr_name, values=[val])
                self._hashes.append({'item': t_res, 'hash': resource})

        self.master.after(self.REDRAW_RATE, self.redraw_devices)

    def __refresh_loop(self):
        """
        Query Brest for available connected devices
        """

        resource_model = ResourceModel()

        while self.refresh:
            if self._connected_devices.qsize() == 0:
                connected_devices = resource_model.get_connected_devices()
                self._is_filling = True
                for device in connected_devices:
                    self._connected_devices.put(device)
                self._is_filling = False
            time.sleep(self.REFRESH_RATE)
