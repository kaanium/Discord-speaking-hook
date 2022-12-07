import win32api
import win32process
import win32con
import ctypes
import pymem.memory
import time
import subprocess
import psutil


def get_process_by_name(process_name):

    process_name = process_name.lower()

    processes = win32process.EnumProcesses()

    for process_id in processes:
        if process_id == -1:
            continue

        try:
            h_process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION
                                             | win32con.PROCESS_VM_READ,
                                             True, process_id)

            try:
                modules = win32process.EnumProcessModules(h_process)

                for address_base in modules:
                    name = str(win32process.GetModuleFileNameEx(h_process,
                                                                address_base))

                    if name.lower().find(process_name) != -1:
                        return process_id, address_base
            finally:
                win32api.CloseHandle(h_process)
        except Exception:
            pass


def read_process_memory(_, address_function, offsets_function):

    h_process = ctypes.windll.kernel32.OpenProcess(win32con.PROCESS_VM_READ,
                                                   False, p_id)

    data = ctypes.c_uint(0)

    bytes_read = ctypes.c_uint(0)

    current_address = address_function

    if offsets_function:
        
        offsets_function.append(None)

        for offset in offsets_function:
            ctypes.windll.kernel32.ReadProcessMemory(h_process,
                                                     current_address,
                                                     ctypes.byref(data),
                                                     ctypes.sizeof(data),
                                                     ctypes.byref(bytes_read))

            if not offset and offset != 0x0:
                return current_address, data.value
            else:
                current_address = data.value + offset

    else:
        ctypes.windll.kernel32.ReadProcessMemory(h_process, current_address,
                                                 ctypes.byref(data),
                                                 ctypes.sizeof(data),
                                                 ctypes.byref(bytes_read))

    ctypes.windll.kernel32.CloseHandle(h_process)

    return current_address, data.value


p_id, base_address = get_process_by_name("discord.exe")

address = base_address + 0x06D6C2F8
offsets = [0x000, 0x1BCC]
pointer_value, value = read_process_memory(p_id, address, offsets)

process = pymem.process
mem = pymem.memory


DMC5 = pymem.Pymem("discord.exe")
DMC5_base = DMC5.process_handle
test = 0
lamp_process = None

while True:
    time.sleep(0.2)
    if 18 != mem.read_int(DMC5_base, pointer_value):
        if test == 0:
            lamp_process = subprocess.Popen(["python.exe", "lamp.pyw", "-l"])
            test = 1
    else:
        if test == 1:
            psutil.Process(lamp_process.pid).kill()
        lamp_process = None
        test = 0
