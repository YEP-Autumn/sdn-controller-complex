namespace cl trpc_packet
namespace cpp trpc_packet
namespace d trpc_packet
namespace dart trpc_packet
namespace java trpc_packet
namespace php trpc_packet
namespace perl trpc_packet
namespace haxe trpc_packet
namespace netstd trpc_packet

typedef i32 MyInteger

const i32 INT32CONSTANT = 9853
const map<string,string> MAPCONSTANT = {'hello':'world', 'goodnight':'moon'}

enum FieldType {
  EthernetII = 1,
  VLAN = 2,
  IPV4 = 3,
  IPv6 = 4,
  TCP  = 5,
  UDP  = 6,
  ICMP = 7
}

struct EthernetII {
    1: string dst,
    2: string src,
    3: i16 type;
}

struct VLAN {
    1: i16 vlan,
    2: i16 type
}

struct IPv4 {
    1: i32 src_ip,
    2: i32 dst_ip
}

union Field {
    1: EthernetII ether,
    2: VLAN vlan,
    3: IPv4 ipv4
}

struct FieldMeta {
  1: FieldType type,
  2: Field field
}

struct Packet {
  1: list<FieldMeta> field_list
}
