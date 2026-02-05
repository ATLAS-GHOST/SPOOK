import glob
import os

def find_nic_pcie_path():
    """Auto-detect NIC's PCIe device path"""
    for device_path in glob.glob('/sys/bus/pci/devices/*'):
        net_path = os.path.join(device_path, 'net')
        if os.path.exists(net_path):
            interfaces = os.listdir(net_path)
            for iface in interfaces:
                if iface != 'lo':
                    return device_path, iface
    return None, None

pcie_path, nic_name = find_nic_pcie_path()
print(f"Found NIC: {nic_name} at {pcie_path}")


def read_pcie_stats(pcie_path):
    stats = {}
    
    try:
        # Buffer overflow + packets dropped
        with open(os.path.join(pcie_path, 'aer_dev_nonfatal')) as f:
            for line in f:
                name, value = line.strip().split()
                if name == 'RxOF':
                    stats[name] = int(value)

    except Exception as e:
        print(f"Error reading PCIe stats: {e}")
    
    return stats


if pcie_path:
    stats = read_pcie_stats(pcie_path)
    for stat, value in stats.items():
        print(f"{stat}: {value}")