from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import Ether, Dot1Q
from scapy.utils import rdpcap, wrpcap


class PcapMk:

    pkt = None

    def add_ethernet(self):

        if self.pkt:
            self.pkt = self.pkt / Ether()
        else:
            self.pkt = Ether()

        return self

    def add_vlan(self):
        if self.pkt:
            self.pkt = self.pkt / Dot1Q()
        else:
            self.pkt = Dot1Q()

        return self

    def add_ipv4(self):
        if self.pkt:
            self.pkt = self.pkt / IP()
        else:
            self.pkt = IP()

        return self

    def make(self, path):
        wrpcap(path, self.pkt)
        self.pkt = None


if __name__ == '__main__':
    pcap = PcapMk()
    pcap.add_ethernet().add_vlan().add_ipv4().make('../../resource/auto_gen.pcap')

    # a = rdpcap('../../resource/test.pcap')
    # print(f'${a[0]}')
    # print(f'{[p for p in a]}')
    # b = Ether()/IP(dst="1.2.3.4") / ICMP()
    #
    # # print(Ether())
    #
    # wrpcap('../../resource/auto_gen.pcap', b)