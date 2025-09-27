class TestData:
    
    device_1 = [
        {'src': {'id': 'device_1', 'port': 12}, 'dst': {'id': 'device_2', 'port': 21}},
        {'src': {'id': 'device_1', 'port': 13}, 'dst': {'id': 'device_3', 'port': 31}},
        # {'src': {'id': 'device_1', 'port': 14}, 'dst': {'id': 'device_4', 'port': 41}}
    ]

    device_2 = [
        {'src': {'id': 'device_2', 'port': 21}, 'dst': {'id': 'device_1', 'port': 12}},
        {'src': {'id': 'device_2', 'port': 23}, 'dst': {'id': 'device_3', 'port': 32}},
        {'src': {'id': 'device_2', 'port': 24}, 'dst': {'id': 'device_4', 'port': 42}},
    ]

    device_3 = [
        {'src': {'id': 'device_3', 'port': 31}, 'dst': {'id': 'device_1', 'port': 13}},
        {'src': {'id': 'device_3', 'port': 32}, 'dst': {'id': 'device_2', 'port': 23}},
        {'src': {'id': 'device_3', 'port': 34}, 'dst': {'id': 'device_4', 'port': 43}},
    ]

    device_4 = [
        {'src': {'id': 'device_4', 'port': 41}, 'dst': {'id': 'device_1', 'port': 14}},
        {'src': {'id': 'device_4', 'port': 42}, 'dst': {'id': 'device_1', 'port': 24}},
        {'src': {'id': 'device_4', 'port': 43}, 'dst': {'id': 'device_1', 'port': 34}},
    ]
