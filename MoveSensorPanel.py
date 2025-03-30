import time
import json
import os
import sys
import subprocess
import ctypes
import win32api
import win32con
import win32gui
from ctypes import wintypes
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw, ImageTk
import pywinauto
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sv_ttk
import base64
from io import BytesIO
import pywinstyles

CONFIG_FILE = "config.json" # Caminho do arquivo de configuração
stop_thread = False  # Flag para parar o thread de monitoramento
WINDOW_CLASS = None
TARGET_MONITOR_KEY = None
refresh_rate = None
monitor_event = threading.Event()
# Ícone da bandeja
ICON_BASE64 = "AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAMMOAADDDgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBlFQDAZRUCwGUVH8BlFWDAZRWhwGUVy8BlFd/AZRXlwGUV5cBlFd/AZRXMwGUVocBlFWDAZRUgwGUVAsBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBlFQDAZRUBwGUVLMBlFYvAZRXLwGUVxMBlFZXAZRVowGUVSsBlFT3AZRU9wGUVSsBlFWjAZRWVwGUVw8BlFcvAZRWLwGUVLMBlFQHAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBlFQDAZRUAwGUVEsBlFXvAZRXTwGUVpsBlFUnAZRURwGUVAcBlFQAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFQHAZRURwGUVScBlFabAZRXTwGUVe8BlFRLAZRUAwGYUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUVAMBlFSrAZRW0wGUVwcBlFUjAZRUGwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUVBsBlFUjAZRXAwGUVtMBlFSrAZRUAwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFQDAZRU0wGUVycBlFZnAZRUYwGUVAMFlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZBUAwGUVAMBlFRjAZRWZwGUVycBlFTTAZRUAwGUVAAAAAAAAAAAAAAAAAMBlFQDAZRUAwGUVKsBlFcnAZRWJwGUVCsBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFQrAZRWJwGUVycBlFSrAZRUAwGUVAAAAAAAAAAAAwGUVAMBlFRLAZRW0wGUVmcBlFQrAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFQrAZRWZwGUVtMBlFRLAZRUAAAAAAMBlFQDAZRcAwGUVe8BlFb/AZRUYwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFRnAZRW/wGUVe8BlFgDAZRUAwGUVAMBlFS3AZRXRwGUVSMBlFQDAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZBUAwGUVAMBlFUnAZRXRwGUVLcBlFQDAZRUAwGUVi8BlFaXAZRUGwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUVBsBlFaXAZRWLwGUVAMBlFSDAZRXKwGUVScBlFQDAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBkFQDAZRUAwGUVSsBlFcrAZRUgwGUVYMBlFcLAZRUSwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBlFQDAZRUSwGUVw8BlFWDAZRWgwGUVlcBlFQDAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAvmAOAL9jEiK+YQ91vmEPib9hEE3AZhYHwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFQDAZRWVwGUVoMBlFcvAZRVowGUVAMFlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwWUUAMBlFQC/YxIkwWgax9KRVf/apXL/yXs09b9jEnjAZhcCwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC/ZRUAwGUVAMBlFWjAZRXLwGUV38BlFUvAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUUCL9jEZ3VmF//+OzY//v15f/rzq3/xXEn5b5hDyzAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUVS8BlFd/AZRXlwGUVPcBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAL9jEQC+YQ9cyXw29fHdwv/79OP/+vPi//fq1f/LgT35vl8MSMBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBlFQDAZRU9wGUV5cBlFeXAZRU9wGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL9lFQDAZRUAv2IRJsJqHNXkvZX/+/Tj//rz4//68eD/5L2U/8NtId6/YhAmwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFT3AZRXlwGUV38BlFUvAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFAi/YhGd1Zlg//ju3P/79OT/9OTM/9qkcP/EbSHmv2MSX8RvIwHAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUVS8BlFd/AZRXMwGUVaMBlFQC/ZhYAAAAAAAAAAAAAAAAAAAAAAMBlFQC/YxIAvmEPW8l7NfXx3cP/+vPi/+nJpv/Ng0H8wGQUuL9iETrCahwBwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGYVAMBlFQDAZRVowGUVy8BlFaLAZRWUwGUVAMBlFQAAAAAAAAAAAAAAAAC/ZRUAwGUVAL9iESbCahzV5b6W//Xmz//bpXL/xG4i575hD3jAZBMRv2MSAMBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUVAMBlFZXAZRWgwGUVYsBlFcLAZRURwGUVAAAAAAAAAAAAAAAAAMBlFQC/ZBMIwGQTndWXXv/oxqH/zYVD/MBkFLi/YhA6wmkbAcBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBlFQDAZRUSwGUVw8BlFWDAZRUiwGUVzMBlFUjAZRUAwGUVAAAAAADAZRUAwGUVAL9kE1vEbyP10pBU/8VxJue+YQ94v2QTEb9jEgDAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADBaBQAwGUVAMBlFUrAZRXKwGUVIMBmFQDAZRWOwGUVpMBlFQXAZRUAAAAAAMBlFQDAZRUmwGUV1cFnGP7AZha4v2IQOsJpGwHAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBlFQDAZRUGwGUVpsBlFYvAZRQAwGUVAMBlFS/AZRXTwGUVSMBlFQDAZRUAwGUVAMBlFWbAZRXjwGUVeMBkExG/YxMAwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUVAMBlFUrAZRXRwGUVLMBlFQDAZRUAwGUVAMBlFX/AZRXAwGUVGcBlFQDAZRUAwGUVFcBlFSbAZRUCwGUVAAAAAAAAAAAAAAAAAMBlFQDAZRUGwGUVBsBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMBlFQDAZRUZwGUVwcBlFXu/ZRUAwGUVAAAAAADAZRUAwGUVFMBlFbfAZRWbwGUVC8BlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADBZxYAwGUVAMBlFWvAZRVrwGUVAMFnFgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAZRUAwGUVC8BlFZvAZRW0wGUVEsBlFQAAAAAAAAAAAMBlFQDAZRUAwGUVK8BlFcrAZRVuwGUVAMBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAMFoFwDAZRUAwGUVksBlFZLAZRUAwWgXAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGUVAMBlFQvAZRWLwGUVycBlFSrAZRUAwGUVAAAAAAAAAAAAAAAAAMBlFQDAZRUAwGUVK8BlFTDAZRUAwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAwWgXAMBlFQDAZRWSwGUVksBlFQDBaBcAAAAAAAAAAAAAAAAAwGUVAMBlFQDAZRUZwGUVm8BlFcrAZRU0wGUVAMBlFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADBaBcAwGUVAMBlFZLAZRWSwGUVAMFoFwAAAAAAwGMVAMBlFQDAZRUGwGUVSsBlFcLAZRW0wGUVKsBlFQDAZRUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMFoFwDAZRUAwGUVksBlFZLAZRUAwGUVAMBlFQHAZRUSwGUVS8BlFajAZRXUwGUVfMBlFRLAZRUAwGUWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwWgXAMBlFQDAZRWRwGUVsMBlFUzAZRVrwGUVmMBlFcbAZRXNwGUVi8BlFSzAZRUBwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADBZxYAwGUVAMBlFXzAZRXxwGUV4cBlFc3AZRWhwGUVYMBlFSDAZRUCwGUVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/4AB//4AAH/8B+A/+D/8H/D//w/h//+Hw///w8f//+OP///xj///8R////gf///4P/wf/D/4D/w/8A/8P/AP/D/gD/w/wA/8P8Af/D+Af/wfAP/4HwP/+I4H//GOH//xxj5/48P+f8Pj/n+H8/5/D//+fB///mA///4Af//+Af8="


def create_icon(size=64, use_custom=True):
    """
    Cria um ícone PNG. Se `use_custom=True`, usa a imagem incorporada como Base64.
    Caso contrário, gera um ícone padrão com um gauge azul.

    :param size: Tamanho do ícone (largura e altura)
    :param use_custom: Se True, usa o ícone incorporado. Se False, gera dinamicamente.
    :return: Objeto PIL.Image
    """
    if use_custom:
        try:
            img_data = base64.b64decode(ICON_BASE64)
            img = Image.open(BytesIO(img_data)).convert("RGBA")
            img = img.resize((size, size), Image.LANCZOS)
            return img
        except Exception as e:
            print(f"Erro ao carregar a imagem embutida: {e}")
    
    # Se der erro ou `use_custom=False`, gera o ícone azul padrão
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))  # Fundo transparente
    draw = ImageDraw.Draw(img)
    
    # Círculo externo (gauge)
    border_width = size // 15
    draw.ellipse(
        (border_width, border_width, size - border_width, size - border_width),
        outline=(30, 120, 210, 255),  # Azul
        width=border_width
    )
    
    # Ponteiro
    center = size // 2
    pointer_color = (30, 120, 210, 255)  # Azul
    pointer_points = [
        (center - size // 15, center),  # Base esquerda
        (center + size // 15, center),  # Base direita
        (center - size // 4, center - size // 4),  # Ponta do ponteiro
    ]
    draw.polygon(pointer_points, fill=pointer_color)

    return img

#Função Para iniciar com o Windows
def set_windows_startup(task_name="MoveSensorPanel", enable=True):
    """
    Ativa ou desativa a inicialização automática do programa com o Windows.

    :param task_name: Nome da tarefa no Agendador do Windows.
    :param enable: Se True, cria a tarefa; se False, remove a tarefa.
    """
    if enable:
        exe_path = sys.executable  # Caminho do executável (.exe ou .py)
        command = (
            f'schtasks /create /tn "{task_name}" /tr "{exe_path}" '
            f'/sc ONLOGON /RL HIGHEST /F /IT'
        )
        msg_success = f"The program will be started automatically with Windows."
        msg_error = f"Error creating the task '{task_name}'."
    else:
        command = f'schtasks /delete /tn "{task_name}" /F'
        msg_success = f"The program will no longer be started automatically with Windows."
        msg_error = f"Error removing the task '{task_name}'."

    try:
        subprocess.run(command, shell=True, check=True)
        print(msg_success)
        messagebox.showinfo("Configuração", msg_success)
    except subprocess.CalledProcessError as e:
        print(msg_error, e)
        messagebox.showerror("Erro", msg_error)

# Função para carregar e salvar configurações
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config():
    config = {
        "window_class": WINDOW_CLASS,
        "target_monitor_key": TARGET_MONITOR_KEY,
        "refresh_rate": refresh_rate,
        "start_windows": start_windows
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def save_settings():
    global WINDOW_CLASS, TARGET_MONITOR_KEY, refresh_rate, start_windows
    WINDOW_CLASS = class_name_entry.get()
    monitor_display = monitor_combobox.get()
    TARGET_MONITOR_KEY = monitor_mapping.get(monitor_display, monitor_display)
    refresh_rate = int(refresh_rate_entry.get() or 3)
    start_windows = start_with_windows_var.get()
    print(f"Nome da Classe: {WINDOW_CLASS}, Monitor: {TARGET_MONITOR_KEY}, Refresh Rate: {refresh_rate} segs")
    save_config()
    start_thread()

# Função para encerrar o programa
def quit_program(icon, item):
    global stop_thread
    stop_thread = True  # Sinaliza para a thread parar
    print("Encerrando o programa...")

    # Aguarde um pouco para garantir que as threads terminem
    """for thread in threading.enumerate():
        if thread is not threading.main_thread():  
            thread.join(timeout=2)  # Dá tempo para encerrar com segurança
    """
    icon.stop()  # Para o ícone da bandeja corretamente
    print("Programa encerrado.")

# Função chamada ao fechar a janela de configurações
def on_closing():
    save_settings()
    root.destroy()    

# Função para criar o ícone da bandeja
def create_tray_icon():
    global icon
    icon_image = create_icon()

    menu = Menu(MenuItem('Configurações', open_settings_gui), MenuItem('Sair', quit_program))
    icon = Icon("WindowMonitor", icon_image, menu=menu)
        
    config = load_config()
    
    if config:
        print("Configuração encontrada! Iniciando monitoramento...")
        global WINDOW_CLASS, TARGET_MONITOR_KEY, refresh_rate
        WINDOW_CLASS = config.get("window_class", "TForm_HWMonitoringSensorPanel")
        TARGET_MONITOR_KEY = config.get("target_monitor_key", "Nenhum Monitor")
        refresh_rate = config.get("refresh_rate", 3)
        start_thread()
    else:
        print("Nenhuma configuração encontrada. Abrindo configurações...")
        open_settings_gui()
    icon.run()

# Função para abrir a GUI de Configurações
def apply_theme_to_titlebar(root):
    version = sys.getwindowsversion()

    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, "#1c1c1c")
    elif version.major == 10:
        pywinstyles.apply_style(root, "dark")

        # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)
        
def open_settings_gui():
    global class_name_entry, monitor_combobox, refresh_rate_entry, monitor_mapping, start_with_windows_var, root
    
    config = load_config()

    root = tk.Tk()
    apply_theme_to_titlebar(root)
    root.title("Move Sensor Panel")
    icon_image = create_icon().convert("RGBA")  # Converte para um formato suportado
    icon_photo = ImageTk.PhotoImage(icon_image)  # Usa ImageTk para criar a imagem
    root.iconphoto(True, icon_photo)
    root.geometry("445x200")
    
    start_with_windows_var = tk.BooleanVar(value=config.get("start_windows", False))

    class_name_label = ttk.Label(root, text="Window Class:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    class_name_entry = ttk.Entry(root, width=30)
    class_name_entry.insert(0, config.get("window_class", "TForm_HWMonitoringSensorPanel"))
    class_name_entry.grid(row=0, column=1, padx=0, pady=5, sticky="ew")

    monitor_label = ttk.Label(root, text="Choose Monitor:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    monitors_display, monitor_mapping = get_available_monitors()
    saved_monitor_key = config.get("target_monitor_key", None) # Verifica se há uma configuração salva para o monitor
    monitor_combobox = ttk.Combobox(root, values=monitors_display, width=30)
    # Se houver monitor salvo, mostra o nome do monitor
    if saved_monitor_key:
        display_str = None
        for item in monitors_display:
            if monitor_mapping[item] == saved_monitor_key:
                monitor_combobox.set(item)
                break
    else:
        # Se não houver configuração, deixa a combobox em branco
        monitor_combobox.set('')

    monitor_combobox.grid(row=1, column=1, padx=0, pady=5, sticky="ew")

    refresh_options = [3, 5, 10, 15]
    refresh_rate_label = ttk.Label(root, text="Refresh Rate (s):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    refresh_rate_entry = ttk.Combobox(root, values=refresh_options, state="readonly", width=3)
    refresh_saved = config.get("refresh_rate")
    if refresh_saved in refresh_options:
        refresh_rate_entry.set(refresh_saved)
    else:
        refresh_rate_entry.current(0)
    refresh_rate_entry.grid(row=2, column=1, padx=0, pady=5, sticky="w")
    
    win_start_chk = ttk.Checkbutton(root, text="Start with Windows", style ="Switch.TCheckbutton", variable=start_with_windows_var, command=lambda: set_windows_startup(enable=start_with_windows_var.get()))
    win_start_chk.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    save_button = ttk.Button(root, text="Save", command=on_closing)
    save_button.grid(row=4, column=1, columnspan=2, pady=20, sticky="nsew")
    
    sv_ttk.use_dark_theme()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

# Função para obter monitores disponíveis
def get_all_monitors():
    monitors = {}

    def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        try:
            monitor_info = win32api.GetMonitorInfo(hMonitor)
            device = win32api.EnumDisplayDevices(monitor_info["Device"], 0)
            key = device.DeviceKey.split("\\")[-1] if device.DeviceKey else "Desconhecido"
            device_name = device.DeviceName.split("\\")[-2] if device.DeviceName else "Desconhecido"
            monitors[key] = {
                "X": monitor_info["Monitor"][0],
                "Y": monitor_info["Monitor"][1],
                "Width": monitor_info["Monitor"][2] - monitor_info["Monitor"][0],
                "Height": monitor_info["Monitor"][3] - monitor_info["Monitor"][1],
                "DeviceName": device_name
            }
        except Exception as e:
            print(f"Erro ao obter monitores: {e}")
        return True

    MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong), ctypes.c_ulong)
    ctypes.windll.user32.EnumDisplayMonitors(0, 0, MonitorEnumProc(callback), 0)
    return monitors

def get_available_monitors():
    monitors = get_all_monitors()
    display_list = []
    mapping = {}
    for key, info in monitors.items():
        monitor_name = info.get("DeviceName", "Desconhecido")
        display_str = f"{key} - {monitor_name} ({info['Width']}x{info['Height']})"
        display_list.append(display_str)
        mapping[display_str] = key
    return display_list, mapping

# Função para monitorar e mover a janela
def start_monitoring():
    global stop_thread
    stop_thread = False

    while not stop_thread:
        hwnd = find_window_by_class(WINDOW_CLASS)
        if hwnd:
            monitor_info = get_all_monitors().get(TARGET_MONITOR_KEY)
            if monitor_info:
                x, y = win32gui.GetWindowRect(hwnd)[:2]
                target_x, target_y = monitor_info["X"], monitor_info["Y"]
                if x != target_x or y != target_y:
                    print("Movendo a janela para o monitor alvo...")
                    win32gui.MoveWindow(hwnd, target_x, target_y, monitor_info["Width"], monitor_info["Height"], True)

        # Aguarda o tempo de refresh ou um evento de mudança de monitor
        if not monitor_event.wait(refresh_rate):
            continue
        else:
            monitor_event.clear()  # Reseta o evento para futuras mudanças
            stop_thread = True
            print("[Monitoramento] Reiniciando devido à mudança nos monitores...")
            time.sleep(refresh_rate)  # Atraso para evitar erro de dispositivos não disponíveis
            start_thread()

def start_thread():
    threading.Thread(target=start_monitoring, daemon=True).start()

# Função para encontrar a janela pela classe
def find_window_by_class(class_name):
    def enum_callback(hwnd, lparam):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == class_name:
            lparam.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(enum_callback, hwnds)
    return hwnds[0] if hwnds else None

# Função para detectar mudanças na configuração dos monitores
def monitor_display_changes():
    """
    Configura um hook de mensagens do Windows para capturar eventos de mudança de monitores.
    Sempre que o evento `WM_DISPLAYCHANGE` for detectado, ele reinicia a thread de monitoramento.
    """
    global stop_thread

    class WindowMonitorHook:
        def __init__(self):
            self.hwnd = None

        def wnd_proc(self, hwnd, msg, wparam, lparam):
            if msg == win32con.WM_DISPLAYCHANGE:
                print("[Monitoramento] Mudança na configuração dos monitores detectada!")
                monitor_event.set()  # Sinaliza para reiniciar o monitoramento
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

        def register_window(self):
            class_name = "MonitorEventListener"
            wnd_class = win32gui.WNDCLASS()
            wnd_class.lpfnWndProc = self.wnd_proc
            wnd_class.lpszClassName = class_name
            wnd_class.hInstance = win32api.GetModuleHandle(None)
            class_atom = win32gui.RegisterClass(wnd_class)
            self.hwnd = win32gui.CreateWindow(class_atom, "MonitorEventWindow", 0, 0, 0, 0, 0, 0, 0, wnd_class.hInstance, None)
            win32gui.PumpMessages()  # Mantém a escuta ativa

    # Criar e rodar o hook em uma thread separada
    monitor_thread = threading.Thread(target=WindowMonitorHook().register_window, daemon=True)
    monitor_thread.start()

#Main function
def main():
    # Criação do ícone da bandeja e monitoramento
    monitor_display_changes()
    create_tray_icon()

if __name__ == "__main__":
    main()