import platform
import subprocess

def run_cmd(cmd):
    return subprocess.check_output(cmd).decode('utf-8').strip()

def get_macos_info():
    return {
        'hostname': run_cmd(['hostname']),
        'os_version': run_cmd(['sw_vers', '-productVersion']),
        'os_build': run_cmd(['sw_vers', '-buildVersion']),
        'hardware_model': run_cmd(['sysctl', '-n', 'hw.model']),
        'memory': run_cmd(['sysctl', '-n', 'hw.memsize']),
        'cpu_brand': run_cmd(['sysctl', '-n', 'machdep.cpu.brand_string']),
        'cpu_logical_cores': run_cmd(['sysctl', '-n', 'hw.logicalcpu']),
        'cpu_physical_cores': run_cmd(['sysctl', '-n', 'hw.physicalcpu']),
    }

def get_linux_info():
    return {
        'hostname': run_cmd(['hostname']),
        'os_version': run_cmd(['lsb_release', '-ds']),
        'hardware_model': run_cmd(['uname', '-m']),
        'memory': run_cmd(['grep', 'MemTotal', '/proc/meminfo']),
        'cpu_brand': run_cmd(['grep', 'model name', '/proc/cpuinfo']).split('\n')[0].split(': ')[1],
        'cpu_logical_cores': run_cmd(['nproc']),
        'cpu_physical_cores': run_cmd(['lscpu', '-p']).count('\n'),
    }

def get_windows_info():
    mem = run_cmd(['systeminfo']).split('Total Physical Memory:')[1].split('\n')[0].strip()
    return {
        'hostname': run_cmd(['hostname']),
        'os_version': f"{platform.win32_ver()[0]} {platform.win32_ver()[1]}",
        'hardware_model': platform.machine(),
        'memory': mem,
        'cpu_brand': run_cmd(['wmic', 'cpu', 'get', 'Name']).split('\n')[1].strip(),
        'cpu_logical_cores': run_cmd(['wmic', 'cpu', 'get', 'NumberOfLogicalProcessors']).split('\n')[1].strip(),
        'cpu_physical_cores': run_cmd(['wmic', 'cpu', 'get', 'NumberOfCores']).split('\n')[1].strip(),
    }

def get_operating_system():
    return platform.system()

def get_system_info():
    system = platform.system()
    common_info = {
        'platform': system,
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }

    platform_info = {
        'Darwin': get_macos_info,
        'Linux': get_linux_info,
        'Windows': get_windows_info,
    }

    return {**common_info, **platform_info.get(system, lambda: {})()}

if __name__ == '__main__':
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f'{key}: {value}')
