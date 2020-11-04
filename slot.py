import re
class Slot:

    is_TypeAddress = r'^LOCAL_(.+?)_ADDRESSES.*$'
    is_Address = r' +ADDRESS +\d+,.*$'
    values_addr = r'(\d+)'
    
    def __init__(self, text):
        [subId, slvId, id, ref, name] = self._get_attr(text[0].rstrip())
        self._subsystem_id = subId
        self._slave_id = slvId
        self._id = id
        self._reference = ref
        self._name = name
        self._address = {}
        self._generate_signals(text[2:])

    @property
    def get_subsystem_id(self):
        return self._subsystem_id

    @property
    def get_slave_id(self):
        return self._slave_id

    @property
    def get_id(self):
        return self._id

    @property
    def description(self):
        info = list()
        for [k,v] in self._address.items():
            for i in v.values():
                item = [self._subsystem_id,self._slave_id,'n',self._id,self._name,k]
                for a in i:
                    item.append(a)
                info.append(item)
        return info
    
    def _get_attr(self, text_):
        items = text_.split(', ')
        subId = items[0].split(' ')[1]
        slvId = items[1].split(' ')[1]
        id = items[2].split(' ')[1]
        ref = items[3]
        name = items[4]
        return [subId, slvId, id, ref, name]

    def _generate_signals(self, text_):
        io_range_id = ""
        for line in text_:
            if self._check_is_typeIOAddress(line):
                io_range_id = self._create_new_io_range(line)
            if self._check_is_rangeAddress(line):
                settings = self._get_typeAddress(list(re.findall(self.values_addr, line)))
                if settings[0] == "BOOL":
                    signal_range = self._generate_boolean_range(io_range_id[0], settings[1], settings[2], settings[3]) 
                    self._set_new_signals_range(io_range_id, signal_range)
                elif settings[0] == "WORD":
                    signal_range = self._generate_word_range(io_range_id[0], settings[1], settings[3])
                    self._set_new_signals_range(io_range_id, signal_range)


    def _check_is_typeIOAddress(self, line):
        m= re.search(self.is_TypeAddress, line)
        if m is not None:
            return True
        return False

    def _check_is_rangeAddress(self,line):
        m= re.search(self.is_Address, line)
        if m is not None:
            return True
        return False

    def _generate_boolean_range(self, typeIO, byteInit, bitInit, quantity):
        out = list()
        byte = byteInit
        bit = bitInit
        for item in range(quantity):
            signal = {'dir': typeIO + str(byte) + "." + str(bit), 'symbol' : ""}
            out.append(signal)
            bit += 1
            if (bit > 7):
                byte += 1
                bit = 0
        return out

    def _generate_word_range(self, typeIO, byteInit, quantity):
        out = list()
        byte = byteInit
        for item in range(quantity):
            signal = {'dir' : typeIO + "W" + str(byte), 'symbol' : ""}
            out.append(signal)
            byte += 2
        return out

    def _set_new_signals_range(self, rangeId, signals):
        self._address[rangeId] = signals

    def _create_new_io_range(self, line):
        typeIO = re.findall(self.is_TypeAddress, line)[0]
        range_list = [key for key, value in self._address if typeIO in key.lower()]



    def _get_typeAddress(self, params):
        pass