import time
from serial import Serial
from xbee import ZigBee


class SensorNet(object):
    def __init__(self, port=None):
        self.port = port
        self.serial = Serial(port)
        time.sleep(1)

        # add exception callback to the event below
        self.xb = ZigBee(self.serial, shorthand=True, callback=self._process_packet, escaped=True)
        self.start_network()
        time.sleep(1)
        self.units = []
        self.command_to_bytes = {'set_pin_mode': b'\x01',
                                 'digital_write': b'\x02',
                                 'digital_read': b'\x03',
                                 'analog_read': b'\x04'}

        self.pinmode_to_bytes = {'DIGITAL_IN': b'\x01\x00',
                                 'DIGITAL_OUT': b'\x02\x00',
                                 'ANALOG_IN': b'\x03\x00',
                                 'PWM': b'\x04\x00',
                                 'DHT': b'\x05\x00'}

    def start_network(self):
        self.xb.send('at', command='ND'.encode('ascii'))

    def _process_packet(self, data):
        print(data)
        if data['id'] == 'at_response':
            self._process_at_response(data)
        elif data['id'] == 'rx':
            self._process_rf_packet(data)
        else:
            pass

    def _process_at_response(self, data):
        if data['command'] == b'ND':
            print("Adding new unit")
            unit = Unit(data['parameter'])
            match = next((x for x in self.units if x.node_identifier == unit.node_identifier), None)
            if match is None:
                self.units.append(unit)
            else:
                self.units.remove(match)
                self.units.append(unit)

        else:
            pass

    def _process_rf_packet(self, data):
        unit = next((x for x in self.units if x.source_addr_long == data['source_addr_long']), None)
        rf_data = data['rf_data']
        for command_name, byte in self.command_to_bytes.items():
            if byte == rf_data[0:1]:
                command = command_name
        pin = int.from_bytes(rf_data[1:2], byteorder='little')
        if command == 'set_pin_mode':
            for mode, byte in self.pinmode_to_bytes.items():
                if byte == rf_data[2:4]:
                    value = mode
        else:
            value = int.from_bytes(rf_data[2:4], byteorder='little')
        self._update_pins(unit, command, pin, value)

    def _update_pins(self, unit, command, pin, value):
        try:
            unit.pins[pin]
        except KeyError:
            unit.pins[pin] = {}
        if command == 'set_pin_mode':
            unit.pins[pin]['mode'] = value
        else:
            unit.pins[pin]['value'] = value

    def send_pin_command(self, unit_name, command, pin, value=None):
        packet = self.command_to_bytes[command]
        packet += (pin).to_bytes(1, byteorder='little')
        if value is not None:
            if isinstance(value, str):
                packet += self.pinmode_to_bytes[value]
            else:
                packet += (value).to_bytes(2, byteorder='little')
        unit = next((x for x in self.units if x.node_identifier == unit_name), None)
        print(packet)
        self.xb.send('tx', dest_addr=unit.source_addr, dest_addr_long=unit.source_addr_long, data=packet)


class Unit(object):
    def __init__(self, paramaters):
        self.paramaters = paramaters
        self.source_addr = self.paramaters['source_addr']
        self.node_identifier = self.paramaters['node_identifier']
        self.source_addr_long = self.paramaters['source_addr_long']
        self.device_type = self.paramaters['device_type']
        self.pins = {}
