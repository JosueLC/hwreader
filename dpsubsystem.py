import re
from dpslave import DPSlave

class DPSubsystem:

    def __init__(self, text):
        [id, name] = self._get_id_name(text[0].rstrip())
        self._id = id
        self._name = name
        self._slaves = {}
 
    @property
    def get_id(self):
        return self._id

    @property
    def description(self):
        data = list()
        for slave in self._slaves:
            data_slave = self._slaves[slave].description
            for addr in data_slave:
                data.append(addr)
        return data

    def get_slave(self, id):
        return self._slaves.get(id, None)

    def set_new_slave(self, slave):
        self._slaves[slave.get_id] = slave

    def _get_id_name(self, text):
        items = text.split(', ')
        id = items[0].split(' ')[1]
        name = items[1]
        return [id, name]