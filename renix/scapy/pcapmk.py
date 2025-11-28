from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import Ether
from scapy.utils import rdpcap, wrpcap

a = rdpcap('../../resource/test.pcap')
print(f'${a[0]}')
print(f'{[p for p in a]}')

b = Ether()/IP(dst="1.2.3.4") / ICMP()

# print(Ether())

wrpcap('../../resource/auto_gen.pcap', b)
