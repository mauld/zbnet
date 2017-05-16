# Sample API ND command response
import zbnet
import time

testunit = {'status': b'\x00', 'parameter': {'source_addr': b'\x96\x13', 'node_identifier': b' ROUTER5', 'status': b'\x00', 'source_addr_long': b'\x00\x13\xa2\x00@\xdc\x8b\xa1', 'parent_address': b'\xff\xfe', 'manufacturer': b'\x10\x1e', 'device_type': b'\x01', 'profile_id': b'\xc1\x05'}, 'frame_id': b'\x01', 'command': b'ND', 'id': 'at_response'}


testdata = {'source_addr': b'\x96\x13', 'rf_data': b'\x01\x01\x01\x00', 'source_addr_long': b'\x00\x13\xa2\x00@\xdc\x8b\xa1', 'id': 'rx', 'options': b'\x01'}

sn = zbnet.SensorNet('/dev/cu.usbserial-DN018RGN')
sn.start_network()
time.sleep(2)
print(len(sn.units))
# sn._process_packet(testunit)
# sn._process_packet(testdata)
sn.send_pin_command(b' ROUTER1', 'digital_read', 1)

print(sn.units[0].pins)
