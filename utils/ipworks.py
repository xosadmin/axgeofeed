import ipaddress

def trimCidr(cidr):
    if "/" in cidr:
        cidr = cidr.split("/")[0]
    return cidr

def is_valid_cidr(cidr):
    try:
        ipaddress.ip_network(cidr)
        return True
    except ValueError:
        return False

def is_valid_ipaddr(ipaddr):
    ipaddr = trimCidr(ipaddr)
    try:
        ipaddress.ip_network(ipaddr)
        return True
    except ValueError:
        return False

def check_ip_version(ipaddr):
    try:
        if "/" in ipaddr:
            ipaddr = ipaddr.split("/")[0]
        ip_obj = ipaddress.ip_address(ipaddr)
        if isinstance(ip_obj, ipaddress.IPv6Address):
            return 6
        elif isinstance(ip_obj, ipaddress.IPv4Address):
            return 4
    except ValueError:
        return False

def compare_ipaddr(ipaddr1,ipaddr2):
    ipaddr1 = ipaddress.ip_address(ipaddr1)
    ipaddr2 = ipaddress.ip_address(ipaddr2)
    if ipaddr1 != ipaddr2:
        return False
    else:
        return True

def compareCIDR(ipaddr,cidr):
    networkobj = ipaddress.ip_network(cidr)
    ipaddr1 = ipaddress.ip_address(ipaddr)
    if ipaddr1 in networkobj:
        return True
    else:
        return False