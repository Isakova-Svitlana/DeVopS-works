#!/usr/bin/python

import re
from jinja2 import Environment, FileSystemLoader
import collections

conffile = open('172.19.20.8.cfg', 'r')
filetext = conffile.read()
conffile.close()


def parse_huawei(filetext):

    sysname = re.findall(r"sysname\s+(.*)\r\n", filetext)

    managment_interface = re.finditer(r"^(interface Vlanif(?P<iface>.*)\r\n)"
                                      r"(.*ip address\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+.*\r\n)",
                                      filetext,
                                      re.MULTILINE)

    vlans = re.finditer(r"(\s+vlan batch\s+(?P<vl>.*)\r\n)",
                        filetext, re.MULTILINE)

    pvid_interface = re.finditer(r"^(interface (?P<iface>.*Ethernet.*)\r\n)"
                                 r"(\s+.*\r\n)*"
                                 r"(.*pvid vlan\s+(?P<pvid>\d+)\r\n)"
                                 r"(\s+.*\r\n)*"
                                 r"(.*port hybrid untagged vlan\s+(?P<untagged>.*)\r\n)",
                                 filetext,
                                 re.MULTILINE)

    tagged_interface = re.finditer(r"^(interface (?P<iface>.*Ethernet.*)\r\n)"
                                   r"(\s+.*\r\n)*"
                                   r"(.*port hybrid tagged vlan\s+(?P<tagged>.*)\r\n)",
                                   filetext,
                                   re.MULTILINE)

    trunk_interface = re.finditer(r"^(interface (?P<iface>.*Ethernet.*)\r\n)"
                                  r"(\s+.*\r\n)*"
                                  r"(\s+.*undo port trunk.*\r\n)"
                                  r"(\s+.*\r\n)*"
                                  r"(.*port trunk allow-pass vlan\s+(?P<trunk>.*)\r\n)",
                                  filetext,
                                  re.MULTILINE)

    ipoe_vlan = re.findall(r"vlan\s(\d+)\r\n"
                           r"\s+description ipoe\r\n",
                           filetext,
                           re.MULTILINE)

    interface = {'sysname': sysname[0]}
    interface['ipoe_vlan'] = ipoe_vlan[0]

    interface['managment'] = {}
    interface['iface'] = {}

    sum_vlans = ""
    for v in vlans:
        sum_vlans = sum_vlans + " " + v.group("vl")

    interface['sum_vlans'] = sum_vlans

    for inter in managment_interface:
        octets = re.findall(r"(\d+\.\d+\.\d+)\.\d+", inter.group("ip"))
        gateway = octets[0] + ".254"
        interface['managment']['vlan'] = inter.group("iface")
        interface['managment']['ip'] = inter.group("ip")
        interface['managment']['gateway'] = gateway

    for inter in pvid_interface:
        un = re.split('\\s+', inter.group("untagged"))
        untagged_vlan = ''
        p = re.findall(r"(.*)Ethernet0\/0\/(\d+)", inter.group("iface"))

        for i in p:
            if i[0] == 'Gigabit':
                port = int(i[1]) + 24
            else:
                port = int(i[1])

        for i in un:
            if i == inter.group("pvid"):
                untagged_vlan = inter.group("pvid")

        interface['iface'][port] = {}
        interface['iface'][port]['untagged'] = untagged_vlan

    for inter in tagged_interface:
        p = re.findall(r"(.*)Ethernet0\/0\/(\d+)", inter.group("iface"))

        for i in p:
            if i[0] == 'Gigabit':
                port = int(i[1]) + 24
            else:
                port = int(i[1])

        # if inter.group("iface") not in interface['iface']:
        if port not in interface['iface']:
            interface['iface'][port] = {}
        interface['iface'][port]['tagged'] = inter.group("tagged")

    for inter in trunk_interface:
        p = re.findall(r"(.*)Ethernet0\/0\/(\d+)", inter.group("iface"))

        for i in p:
            if i[0] == 'Gigabit':
                port = int(i[1]) + 24
            else:
                port = int(i[1])

        if port not in interface['iface']:
            interface['iface'][port] = {}
        interface['iface'][port]['trunk'] = inter.group("trunk")

    result = collections.OrderedDict(sorted(interface.items()))
    return result


def generate_config(data, tmpl, ending):
    env = Environment(loader=FileSystemLoader('/home/kbn/bin/sw/templates'),
                      trim_blocks=True,
                      lstrip_blocks=True,
                      newline_sequence=new_line
                      )

    template = env.get_template(tmpl)

    fname = 'gcom.conf'
    with open(fname, 'w') as f:
        cfg = template.render(interface=data)
        f.write(cfg)


res = parse_huawei(filetext)
new_line = '\r\n'  # for huawei and gcom new line "\r\n"

# generate_config(res, 'edge-core.j2', new_line)
generate_config(res, 'gcom.j2', new_line)
