# LCARS Framework :: System Monitor Utilities v1.0.0
# Моніторинг системних ресурсів
# Автор: LCARS Development Team
# Ліцензія: MIT

__version__ = "1.0.0"
__author__ = "LCARS Development Team"
__license__ = "MIT"

import psutil
from typing import Dict, List, Optional, Tuple
from time import time
import threading
from lcars.base.version import getVersion

version = getVersion()
# print(f"LCARS System Monitor v{version}")  # Вимкнено для UI

class Monitor:
    # Монітор системних ресурсів
    
    def __init__(self):
        self.start_time = time()
        self.last_network = None
    
    def cpu_info(self) -> Dict:
        # Інформація про CPU
        return {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'count_logical': psutil.cpu_count(logical=True),
            'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    def memory_info(self) -> Dict:
        # Інформація про пам'ять
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'memory': {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'free': mem.free,
                'percent': mem.percent
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
        }
    
    def disk_info(self) -> List[Dict]:
        # Інформація про диски
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                })
            except:
                continue
        return disks
    
    def network_info(self) -> Dict:
        # Інформація про мережу
        net_io = psutil.net_io_counters()
        net_addrs = psutil.net_if_addrs()
        net_stats = psutil.net_if_stats()
        
        # Розраховуємо швидкість
        current_time = time()
        speed = {'bytes_sent_per_sec': 0, 'bytes_recv_per_sec': 0}
        
        if self.last_network:
            time_diff = current_time - self.last_network['time']
            if time_diff > 0:
                speed['bytes_sent_per_sec'] = (net_io.bytes_sent - self.last_network['bytes_sent']) / time_diff
                speed['bytes_recv_per_sec'] = (net_io.bytes_recv - self.last_network['bytes_recv']) / time_diff
        
        self.last_network = {
            'time': current_time,
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv
        }
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'speed': speed,
            'interfaces': list(net_addrs.keys()),
            'active_interfaces': [name for name, stats in net_stats.items() if stats.isup]
        }
    
    def process_info(self, pid: Optional[int] = None) -> Dict:
        # Інформація про процеси
        if pid is None:
            pid = psutil.Process().pid
        
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'memory_info': proc.memory_info()._asdict(),
                'create_time': proc.create_time(),
                'num_threads': proc.num_threads(),
                'connections': len(proc.connections()),
                'cmdline': proc.cmdline()
            }
        except:
            return {}
    
    def all_processes(self) -> List[Dict]:
        # Всі процеси
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                continue
        return processes
    
    def system_info(self) -> Dict:
        # Повна системна інформація
        boot_time = psutil.boot_time()
        
        return {
            'boot_time': boot_time,
            'uptime': time() - boot_time,
            'users': [{'name': user.name, 'terminal': user.terminal, 'host': user.host} 
                     for user in psutil.users()],
            'processes_count': len(psutil.pids()),
            'threads_count': sum(proc.num_threads() for proc in psutil.process_iter() 
                               if hasattr(proc, 'num_threads'))
        }
    
    def temperature_info(self) -> Optional[Dict]:
        # Інформація про температуру
        if hasattr(psutil, 'sensors_temperatures'):
            temps = psutil.sensors_temperatures()
            return {name: [{'label': t.label, 'current': t.current, 'high': t.high, 'critical': t.critical} 
                          for t in sensors] for name, sensors in temps.items()}
        return None
    
    def battery_info(self) -> Optional[Dict]:
        # Інформація про батарею
        if psutil.sensors_battery():
            battery = psutil.sensors_battery()
            return {
                'percent': battery.percent,
                'secsleft': battery.secsleft,
                'power_plugged': battery.power_plugged
            }
        return None
    
    def get_alerts(self) -> List[str]:
        # Системні попередження
        alerts = []
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        # Memory
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            alerts.append(f"High memory usage: {mem.percent:.1f}%")
        
        # Disk
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if (usage.used / usage.total) * 100 > 90:
                    alerts.append(f"Low disk space on {partition.mountpoint}: {(usage.used / usage.total) * 100:.1f}%")
            except:
                continue
        
        # Temperature
        temps = self.temperature_info()
        if temps:
            for name, sensors in temps.items():
                for sensor in sensors:
                    if sensor['critical'] and sensor['current'] > sensor['critical']:
                        alerts.append(f"Critical temperature: {name} {sensor['label']} - {sensor['current']}°C")
        
        return alerts

class RealTimeMonitor:
    # Моніторинг в реальному часі
    
    def __init__(self, update_interval: float = 1.0):
        self.monitor = Monitor()
        self.update_interval = update_interval
        self.running = False
        self.callbacks = []
        self.thread = None
    
    def add_callback(self, callback):
        # Додати callback для отримання даних
        self.callbacks.append(callback)
    
    def start(self):
        # Почати моніторинг
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        # Зупинити моніторинг
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _monitor_loop(self):
        # Цикл моніторингу
        while self.running:
            data = {
                'timestamp': time(),
                'cpu': self.monitor.cpu_info(),
                'memory': self.monitor.memory_info(),
                'network': self.monitor.network_info(),
                'alerts': self.monitor.get_alerts()
            }
            
            for callback in self.callbacks:
                callback(data)
            
            import time as time_module
            time_module.sleep(self.update_interval)

# Швидкі функції
def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=1)

def get_memory_usage() -> Dict:
    mem = psutil.virtual_memory()
    return {'total': mem.total, 'used': mem.used, 'percent': mem.percent}

def get_disk_usage(path: str = '/') -> Dict:
    usage = psutil.disk_usage(path)
    return {'total': usage.total, 'used': usage.used, 'free': usage.free, 'percent': (usage.used / usage.total) * 100}

def get_network_stats() -> Dict:
    net_io = psutil.net_io_counters()
    return {'bytes_sent': net_io.bytes_sent, 'bytes_recv': net_io.bytes_recv}

def check_system_health() -> List[str]:
    monitor = Monitor()
    return monitor.get_alerts()
