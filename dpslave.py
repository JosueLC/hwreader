import re
from slot import Slot

class DPSlave():
    is_Comment = r'( COMMENT )'

    def __init__(self, text):
        [subId, id, ref, name] = self._get_attr(text[0].rstrip())
        self._subsystem_id = subId
        self._id = id
        self._reference = ref
        self._name = name
        self._comment = self._get_comment(text)
        self._slots = {}

    @property
    def get_id(self):
        return self._id

    @property
    def get_subsystem_id(self):
        return self._subsystem_id
    
    @property
    def description(self):
        data = list()
        #primera linea para el equipo, las siguientes para los slots
        for slot in self._slots:
            data_slot = self._slots[slot].description
            for addr in data_slot:
                addr['nombre_equipo'] = self._name.replace('"','')
                addr['ref_equipo'] = self._reference.replace('"','')
                addr['comentario'] = self._comment.replace('"','')
                data.append(addr)
        return data

    def get_slot(self, id):
        return self._slots[id]

    def _get_attr(self, text):
        items = text.split(', ')
        subId = items[0].split(' ')[1]
        id = items[1].split(' ')[1]
        ref = items[2]
        name = items[3]
        return [subId, id, ref, name]
    
    def _get_comment(self,text):
        for line in text:
            m= re.search(self.is_Comment, line)
            if m is not None:
                t = re.findall(r'\"(.+?)\"',line)
                if len(t) > 0:
                    return t[0]
        return ""

    def set_new_slot(self, slot):
        self._slots[slot.get_id] = slot