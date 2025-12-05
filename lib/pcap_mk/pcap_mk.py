from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import Ether, Dot1Q
from scapy.utils import rdpcap, wrpcap


class PcapMk:

    pkt = None

    def add_ethernet(self, src, dst):

        if self.pkt:
            self.pkt = self.pkt / Ether(src=src, dst=dst)
        else:
            self.pkt = Ether(src=src, dst=dst)

        return self

    def add_vlan(self, vlan):
        if self.pkt:
            self.pkt = self.pkt / Dot1Q(vlan=vlan)
        else:
            self.pkt = Dot1Q(vlan=vlan)

        return self

    def add_ipv4(self, src, dst):
        if self.pkt:
            self.pkt = self.pkt / IP(src=src, dst=dst)
        else:
            self.pkt = IP(src=src, dst=dst)

        return self

    def make(self, path):
        wrpcap(path, self.pkt)
        self.pkt = None


if __name__ == "__main__":
    pcap = PcapMk()
    pcap.add_ethernet("00:11:22:33:44:05", "00:11:22:33:44:06").add_vlan(100).add_ipv4(
        "1.2.3.4", "2.2.2.2"
    ).make("../../resource/auto_gen.pcap")

    # a = rdpcap('../../resource/test.pcap')
    # print(f'${a[0]}')
    # print(f'{[p for p in a]}')
    # b = Ether()/IP(dst="1.2.3.4") / ICMP()
    #
    # # print(Ether())
    #
    # wrpcap('../../resource/auto_gen.pcap', b)
