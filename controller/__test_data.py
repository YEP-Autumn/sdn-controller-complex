class TestData:

    device_1 = {
        'hostname': 'device_1',
        'interconnection_links': [
            {'from': {'hostname': 'device_2', 'port': 21}, 'to': {'hostname': 'device_1', 'port': 12}},
            {'from': {'hostname': 'device_3', 'port': 31}, 'to': {'hostname': 'device_1', 'port': 13}},
            # {'from': {'hostname': 'device_4', 'port': 41}, 'to': {'hostname': 'device_1', 'port': 14}},
        ],
        'ports': [
            {'port_no':1},
            {'port_no':2},
            {'port_no':3},
            {'port_no':4}   
        ]
    }

    device_2 = {
        'hostname': 'device_2',
        'interconnection_links': [
            {'from': {'hostname': 'device_1', 'port': 12}, 'to': {'hostname': 'device_2', 'port': 21}},
            {'from': {'hostname': 'device_3', 'port': 32}, 'to': {'hostname': 'device_2', 'port': 23}},
            {'from': {'hostname': 'device_4', 'port': 42}, 'to': {'hostname': 'device_2', 'port': 24}},
        ],
        'ports': [
            {'port_no':1},
            {'port_no':2},
            {'port_no':3},
            {'port_no':4}   
        ]
    }

    device_3 = {
        'hostname': 'device_3',
        'interconnection_links': [
            {'from': {'hostname': 'device_1', 'port': 13}, 'to': {'hostname': 'device_3', 'port': 31}},
            {'from': {'hostname': 'device_2', 'port': 23}, 'to': {'hostname': 'device_3', 'port': 32}},
            {'from': {'hostname': 'device_4', 'port': 43}, 'to': {'hostname': 'device_3', 'port': 34}},
        ],
        'ports': [
            {'port_no':1},
            {'port_no':2},
            {'port_no':3},
            {'port_no':4}   
        ]
    }

    device_4 = {
        'hostname': 'device_4',
        'interconnection_links': [
            {'from': {'hostname': 'device_1', 'port': 14}, 'to': {'hostname': 'device_4', 'port': 41}},
            {'from': {'hostname': 'device_2', 'port': 24}, 'to': {'hostname': 'device_4', 'port': 42}},
            {'from': {'hostname': 'device_3', 'port': 34}, 'to': {'hostname': 'device_4', 'port': 43}},
        ],
        'ports': [
            {'port_no':1},
            {'port_no':2},
            {'port_no':3},
            {'port_no':4}   
        ]
    }
