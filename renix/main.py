from renix_py_api.renix import *
import time

initialize(log_level=logging.INFO)


def send_stream():
    port = Port(upper=sys_entry, Location='//192.168.2.11/5/13')
    assert port.handle

    bring_port_online_cmd = BringPortsOnlineCommand(PortList=[port.handle])
    bring_port_online_cmd.execute()

    create_stream_from_pcap_cmd = CreateStreamFromPcapCommand(PortList=[port.handle], FilePath="../resource/test.pcap")
    create_stream_from_pcap_cmd.execute()

    stream_port_config = port.get_children(StreamPortConfig.cls_name())[0]
    assert stream_port_config
    assert stream_port_config.handle


    # 配置burst模式
    # stream_port_config.edit(TransmitMode=EnumTransmitMode.BURST)
    # stream_port_burst_cfgs = stream_port_config.get_children(BurstTransmitConfig.cls_name())
    # stream_port_burst_cfg = stream_port_burst_cfgs[0]
    # stream_port_burst_cfg.edit(FramePerBurst=100, BurstCount=1)

    # 配置step模式
    stream_port_config.edit(TransmitMode=EnumTransmitMode.STEP)
    step_trans_config = stream_port_config.get_children(StepTransmitConfig.cls_name())[0]
    step_trans_config.edit(Frames=50)


    stream = port.get_children(StreamTemplate.cls_name())[0]

    update_header_cmd = UpdateHeaderCommand(Stream=stream.handle,
                                            Parameter='ethernetII_1.sourceMacAdd=00:01:01:a0:00:01 '
                                                      'ipv4_1.destination=10.10.0.1 '
                                                      'ipv4_1.checksum=auto '
                                                      'ipv4_1.source.XetModifier:a.StreamType=InterModifier '
                                                      'ipv4_1.source.XetModifier:a.Type=Increment '
                                                      'ipv4_1.source.XetModifier:a.Start=10.10.1.1 '
                                                      'ipv4_1.source.XetModifier:a.Step=1 '
                                                      'ipv4_1.source.XetModifier:a.Count=50')
    update_header_cmd.execute()

    start_stream_cmd = StartStreamCommand(StreamList=[stream.handle])
    start_stream_cmd.execute()
    # start_all_stream_cmd = StartAllStreamCommand()
    # start_all_stream_cmd.execute()


def start_capture():
    port = Port(upper=sys_entry, Location='//192.168.2.11/5/14')
    assert port.handle

    bring_port_online_cmd = BringPortsOnlineCommand(PortList=[port.handle])
    bring_port_online_cmd.execute()

    cap_conf = port.get_children(CaptureConfig.cls_name())[0]
    start_cap_cmd = StartCaptureCommand(CaptureConfigs=cap_conf.handle)
    start_cap_cmd.execute()

    send_stream()

    time.sleep(2)

    stop_cap_cmd = StopCaptureCommand(CaptureConfigs=cap_conf.handle)
    stop_cap_cmd.execute()

    download_cap_data_cmd = DownloadCaptureDataCommand(CaptureConfigs=cap_conf.handle, FileDir='../resource/temp/',
                                                       FileName='test.pcap', MaxDownloadDataCount=50)

    download_cap_data_cmd.execute()


if __name__ == '__main__':
    sys_entry = get_sys_entry()

    start_capture()

    time.sleep(3)
