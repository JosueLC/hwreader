import re
class Slot:

    is_TypeAddress = r'^LOCAL_(.+?)_ADDRESSES.*$'
    is_Address = r' +ADDRESS +\d+,.*$'
    values_addr = r'(\d+)'
    is_Symbol = r'^SYMBOL.*$'
    is_Parameter = r'^PARAMETER$'
    is_Param_Type = r'(?=_TYPE).*'
    is_Param_Range = r'(?=_RANGE).*'
    
    def __init__(self, text):
        [subId, slvId, id, ref, name] = self._get_attr(text[0].rstrip())
        self._subsystem_id = subId
        self._slave_id = slvId
        self._id = id
        self._reference = ref
        self._name = name
        self._address = {}
        self._generate_signals(text[2:])
        self._get_symbols(text[2:])
        self._get_parameters(text[2:])

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
        base = {'red': self._subsystem_id,
                'dir_profibus': self._slave_id,
                'slot_modulo': self._id,
                'ref_modulo': self._reference,
                'nombre_modulo': self._name
                }
        for range_id in self._address:
            for io_dir in self._address[range_id]:
                info.append(base | self._address[range_id][io_dir])    
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
            elif self._check_is_rangeAddress(line):
                settings = self._get_typeAddress(list(re.findall(self.values_addr, line)))
                if settings[0] == "BOOL":
                    signal_range = self._generate_boolean_range(io_range_id[0], settings[1], settings[2], settings[3]) 
                    self._set_new_signals_range(io_range_id, signal_range)
                elif settings[0] == "WORD":
                    signal_range = self._generate_word_range(io_range_id[0], settings[1], settings[3],settings[4])
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

    def _check_is_Symbol(self,line):
        m= re.search(self.is_Symbol, line)
        if m is not None:
            return True
        return False

    def _check_is_parameter(self,line):
        m= re.search(self.is_Parameter, line)
        if m is not None:
            return True
        return False

    def _generate_boolean_range(self, typeIO, byteInit, bitInit, quantity):
        out = dict()
        byte = 0
        bit = 0
        #cambia la 'O'(OUT) por 'Q'
        typeIO = 'Q' if typeIO=='O' else typeIO
        for _ in range(quantity):
            signal = {'dir': typeIO + str(byte + byteInit) + "." + str(bit + bitInit), 'tag' : ""}
            out[str(bit + (8*byte))] = signal
            bit += 1
            if (bit > 7):
                byte += 1
                bit = 0
        return out

    def _generate_word_range(self, typeIO, byteInit, quantity,step):
        out = dict()
        byte = 0
        pos = 0
        #cambia la 'O'(OUT) por 'Q'
        typeIO = 'Q' if typeIO=='O' else typeIO
        for _ in range(quantity):
            signal = {'dir' : typeIO + "W" + str(byte + byteInit), 'tag' : ""}
            out[str(pos)] = signal
            byte += 2
            pos += step
        return out

    def _set_new_signals_range(self, rangeId, signals):
        if len(self._address[rangeId]) == 0:
            self._address[rangeId] = signals
        else:
            self._address[rangeId].extend(signals)

    def _create_new_io_range(self, line):
        typeIO = re.findall(self.is_TypeAddress, line)[0]
        range_list = [key for key, value in self._address.items() if typeIO in key]
        if len(range_list) > 0:
            range_list = [int(re.findall(r'[0-9]+', key)[0]) for key in range_list]
            newId = typeIO + str(1 + max(range_list))
        else:
            newId = typeIO + str(0)
        self._address[newId] = {}
        return newId

    def _get_typeAddress(self, params):
        byteInit = int(params[0])
        bitInit = int(params[1])
        quantity = int(params[2])
        typePar2 = int(params[5])
        data_output = ['None',0,0,0,0]

        #Diagnostic
        if quantity == 0:
            data_output = ["NA",0,0,0,0]
        #IOs
        elif typePar2 == 32:
            data_output = ["WORD", byteInit, bitInit, quantity//2,1]
        elif typePar2 == 16:
            data_output = ["BOOL", byteInit, bitInit, quantity,1]
        elif typePar2 == 0:
            ref = re.findall(r'6ES7 (3\d\d)-.*', self._reference)
            if len(ref) > 0:
                num = int(ref[0])
                if num < 330: #BOOL
                    data_output = ["BOOL", byteInit, bitInit, quantity * 8,1]
                elif num > 330: #WORD
                    data_output = ["WORD", byteInit, bitInit, quantity//2,1]
            else: #Special Module (WORD)
                data_output = ["WORD", byteInit, bitInit, quantity//2,2]
        return data_output
    
    def _get_symbols(self,text):
        for line in text:
            if self._check_is_Symbol(line):
                data = line.split(", ")
                rangeAdd = (data[0].replace(" ","-")).split("-")[2]
                rangeAdd="IN0" if rangeAdd == "I" else "OUT0"
                self._address[rangeAdd][data[1]]['tag'] = data[2].replace('"','')
                self._address[rangeAdd][data[1]]['descripcion'] = data[3].replace('"','')

    def _get_parameters(self,text):
        for line in text:
            if re.search(self.is_Param_Type, line) is not None:
                data = line.split(", ")
                typeAdd = data[0].split("_")
                if re.search(r'(?=AI)',typeAdd[0]) is not None:
                    self._address["IN0"][data[-2]]['tipo'] = data[-1].replace('"','')
                if re.search(r'(?=AO)',typeAdd[0]) is not None:
                    self._address["OUT0"][data[-2]]['tipo'] = data[-1].replace('"','')
            if re.search(self.is_Param_Range, line) is not None:
                data = line.split(", ")
                typeAdd = data[0].split("_")
                if re.search(r'(?=AI)',typeAdd[0]) is not None:
                    self._address["IN0"][data[-2]]['rango'] = data[-1].replace('"','')
                if re.search(r'(?=AO)',typeAdd[0]) is not None:
                    self._address["OUT0"][data[-2]]['rango'] = data[-1].replace('"','')