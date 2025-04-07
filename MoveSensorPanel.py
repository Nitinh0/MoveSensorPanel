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


"""--====================VARIAVEIS====================--"""

user32 = ctypes.windll.user32

CONFIG_FILE = "config.json" # Caminho do arquivo de configuração
stop_thread = False  # Flag para parar o thread de monitoramento
WINDOW_CLASS = None
TARGET_MONITOR_KEY = None
monitor_event = threading.Event()
correction_thread = None
monitor_thread = None
lock_mouse = False
start_windows = False
cursor_locker = None
root = None

# Ícone da bandeja
ICON_BASE64 = "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"
icon = None


"""--====================Funções====================--"""

# Gestão de Configurações
def manage_config(action="load", settings=None):
    global WINDOW_CLASS, TARGET_MONITOR_KEY, start_windows, lock_mouse

    if action == "load":
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                WINDOW_CLASS = config.get("window_class", "")
                TARGET_MONITOR_KEY = config.get("target_monitor_key", "")
                start_windows = config.get("start_windows", False)
                lock_mouse = config.get("lock_mouse", False)
                return config
        return {}

    elif action == "save" and settings:
        # Carrega o config atual (se existir)
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        else:
            config = {}

        # Atualiza apenas as chaves fornecidas
        config.update(settings)

        # Salva o novo config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    
    elif action == "update":
        WINDOW_CLASS = class_name_entry.get()
        monitor_display = monitor_combobox.get()
        TARGET_MONITOR_KEY = monitor_mapping.get(monitor_display, monitor_display)
        start_windows = start_with_windows_var.get()
        lock_mouse = lock_mouse_var.get()
        print(f"Nome da Classe: {WINDOW_CLASS}, Monitor: {TARGET_MONITOR_KEY}")
        
        settings = {
            "window_class": WINDOW_CLASS,
            "target_monitor_key": TARGET_MONITOR_KEY,
            "start_windows": start_windows,
            "lock_mouse": lock_mouse
        }
        manage_config("save", settings)

#Função Para iniciar com o Windows
def set_windows_startup(task_name="MoveSensorPanel", enable=True):
    #Ativa ou desativa a inicialização automática do programa com o Windows.

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

# Função para obter monitores disponíveis       
def get_monitors_info():
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

    # Criar lista de exibição e mapeamento
    display_list = []
    mapping = {}
    for key, info in monitors.items():
        monitor_name = info.get("DeviceName", "Desconhecido")
        display_str = f"{key} - {monitor_name} ({info['Width']}x{info['Height']})"
        display_list.append(display_str)
        mapping[display_str] = key

    return monitors, display_list, mapping

# Função para verificar se a janela está fora do monitor
def check_window(class_name, target_monitor):
    def enum_callback(hwnd, lparam):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd) == class_name:
            x, y = win32gui.GetWindowRect(hwnd)[:2] # Recolhe coordenadas X,Y da janela
            
            #Verificar se está fora do monitor
            if x != target_monitor["X"] or y != target_monitor["Y"]:
                lparam.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(enum_callback, hwnds)
    return hwnds[0] if hwnds else None # Retorna janela se estiver fora do monitor, senão ignora "None"

# Função para mover a janela
def move_window(hwnd, target_monitor):    
    if hwnd:
        target_x, target_y = target_monitor["X"], target_monitor["Y"]
        rect = win32gui.GetWindowRect(hwnd)
        width = rect[2] - rect[0]  # Largura atual
        height = rect[3] - rect[1]  # Altura atual
        
        print("Movendo a janela para o monitor alvo...", target_monitor)
        win32gui.MoveWindow(hwnd, target_x, target_y, width, height, True)

#Configura um hook de mensagens do Windows para capturar eventos
class WindowMonitorHook:
    def __init__(self):
        self.hwnd = None

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_CLOSE:
            print("[Monitoramento] Fechando janela invisível de eventos.")
            win32gui.DestroyWindow(hwnd)
        elif msg == win32con.WM_DISPLAYCHANGE:
            print("[Monitoramento] Mudança na configuração dos monitores detectada!")
            monitor_event.set()
        elif msg == win32con.WM_POWERBROADCAST and wparam == win32con.PBT_APMRESUMEAUTOMATIC:
            print("[Monitoramento] Sistema retornou da suspensão!")
            monitor_event.set()
    
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

def monitor_and_correct_window(class_name, target_monitor):
    while not stop_thread:
        monitor_event.wait()  # Espera uma mudança nos monitores ou retorno da suspensão
        monitor_event.clear()  # Reseta o evento para aguardar novas mudanças
        
        if stop_thread:
            break
        
        set_cursorlock()

        monitors, _, _ = get_monitors_info() # Actualiza os monitores disponiveis
        target_monitor = monitors.get(TARGET_MONITOR_KEY, None)
            
        if target_monitor is None:
            print(f"Monitor alvo '{TARGET_MONITOR_KEY}' não encontrado ou indisponível.")
            available_monitors = [monitor for monitor in monitors.values()]
            target_monitor = available_monitors[0]
            if available_monitors:
                target_monitor = available_monitors[0]  # Seleciona o primeiro monitor disponível
                print(f"Movendo para o monitor disponível: {target_monitor}")
            else:
                print("Nenhum monitor disponível encontrado!")
                continue  # Continua aguardando novos eventos
           
        hwnd = check_window(class_name, target_monitor)
        while hwnd:
            move_window(hwnd, target_monitor)
            time.sleep(1)
            hwnd = check_window(class_name, target_monitor)
            print("Recheck")
        print("Janela já se enccontra no Monitor alvo")

# Inicia a thread que corrige a posição da janela sempre que necessário
def start_correction_thread(class_name, target_monitor):
    global correction_thread

    correction_thread = threading.Thread(target=monitor_and_correct_window, args=(class_name, target_monitor), daemon=True)
    correction_thread.start()
    print("Thread de monitoramento iniciada.")
    monitor_event.set()

def stop_correction_thread():
    global stop_thread
    stop_thread = True  # Configura a flag de parada
    monitor_event.set()
    correction_thread.join()  # Espera a thread ser finalizada corretamente)
    stop_thread = False
    print("Thread de monitoramento parada.")

# Ligar/desligar bloqueio do rato
def set_cursorlock():
    global cursor_locker
        
    if cursor_locker is None:
        cursor_locker = CursorLocker(locked_monitor_key=TARGET_MONITOR_KEY)

    if lock_mouse:
        cursor_locker.start_lock()
    else:
        cursor_locker.unlock_cursor()
        cursor_locker = None

class CursorLocker:
    def __init__(self, locked_monitor_key):
        self.locked_monitor_key = locked_monitor_key
        self._stop_event = threading.Event()
        self._thread = None

    def get_cursor_area(self):
        rect = ctypes.wintypes.RECT()
        user32.GetClipCursor(ctypes.byref(rect))
        return (rect.left, rect.top, rect.right, rect.bottom)

    def set_clip_cursor(self, allowed_area):
        rect_struct = ctypes.wintypes.RECT(*allowed_area)
        user32.ClipCursor(ctypes.byref(rect_struct))
        print(f"Rato bloqueado na área: {allowed_area}")

    def unlock_cursor(self):
        self._stop_event.set()  # Sinaliza que o loop deve parar
        if self._thread and self._thread.is_alive():
           print("Aguarde a thread terminar...")
           self._thread.join()
        user32.ClipCursor(None)  # Desbloqueia o cursor
        print("Rato desbloqueado")

    def get_desktop_area(self):
        monitors, _, _ = get_monitors_info()

        all_x = [info["X"] for info in monitors.values()]
        all_y = [info["Y"] for info in monitors.values()]
        all_x_max = [info["X"] + info["Width"] for info in monitors.values()]
        all_y_max = [info["Y"] + info["Height"] for info in monitors.values()]

        return (min(all_x), min(all_y), max(all_x_max), max(all_y_max))

    def get_allowed_area(self):
        monitors, _, _ = get_monitors_info()

        if self.locked_monitor_key not in monitors or len(monitors) <= 1:
            print("Monitor não encontrado ou apenas um monitor disponível.")
            return

        allowed_x = [info["X"] for key, info in monitors.items() if key != self.locked_monitor_key]
        allowed_y = [info["Y"] for key, info in monitors.items() if key != self.locked_monitor_key]
        allowed_x_max = [info["X"] + info["Width"] for key, info in monitors.items() if key != self.locked_monitor_key]
        allowed_y_max = [info["Y"] + info["Height"] for key, info in monitors.items() if key != self.locked_monitor_key]

        if not allowed_x or not allowed_y or not allowed_x_max or not allowed_y_max:
            print("Erro: Área válida não encontrada.")
            return

        return (min(allowed_x), min(allowed_y), max(allowed_x_max), max(allowed_y_max))

    def monitor_loop(self, allowed_area):
        desktop_area = self.get_desktop_area()

        while not self._stop_event.is_set():  # O loop só continua enquanto o evento não for sinalizado
           print("Thread monitorando...")  # Verificação para garantir que o loop está ativo
           current_clip_area = self.get_cursor_area()

           if current_clip_area != desktop_area and current_clip_area != allowed_area:
             print("Outro programa está a controlar o cursor. Pausando bloqueio...")
           elif current_clip_area != allowed_area:
               print("ClipCursor foi desativado! Reaplicando...")
               self.set_clip_cursor(allowed_area)

           time.sleep(1)

    
    def start_lock(self):
        allowed_area = self.get_allowed_area()

        if allowed_area is None:
            print("Área permitida não encontrada.")
            return

        self._stop_event.clear()  # Limpa o evento antes de começar o bloqueio
        self._thread = threading.Thread(target=self.monitor_loop, args=(allowed_area,))
        self._thread.daemon = True
        self._thread.start()


"""--====================Funções GUI====================--"""

def create_icon(size=64, use_custom=True):
    """
    Cria um ícone PNG. Se `use_custom=True`, usa a imagem incorporada como Base64.
    :param use_custom: Se True, usa o ícone incorporado. Se False, gera dinamicamente.
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

# Dark Theme para Titulo da janela
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

# Janela de Settings        
def settings_gui():
    global class_name_entry, monitor_combobox, monitor_mapping, start_with_windows_var, lock_mouse_var, root
    
    config = manage_config("load")

    if root and root.winfo_exists():
        root.deiconify()
        root.lift()
        root.focus_force()
        return

    root = tk.Tk()
    apply_theme_to_titlebar(root)
    root.title("Move Sensor Panel")
    icon_image = create_icon().convert("RGBA")
    icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, icon_photo)
    root.geometry("445x215")
    
    start_with_windows_var = tk.BooleanVar(value=config.get("start_windows", False))
    lock_mouse_var = tk.BooleanVar(value=config.get("lock_mouse", False))

    class_name_label = ttk.Label(root, text="Window Class:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    class_name_entry = ttk.Entry(root, width=30)
    class_name_entry.insert(0, config.get("window_class", "TForm_HWMonitoringSensorPanel"))
    class_name_entry.grid(row=0, column=1, padx=0, pady=5, sticky="ew")

    monitor_label = ttk.Label(root, text="Choose Monitor:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    _, monitors_display, monitor_mapping = get_monitors_info()
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
    
    win_start_chk = ttk.Checkbutton(root, text="Start with Windows", style ="Switch.TCheckbutton", variable=start_with_windows_var, command=lambda: set_windows_startup(enable=start_with_windows_var.get()))
    win_start_chk.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    lock_mouse = ttk.Checkbutton(root, text="Lock Mouse", style ="Switch.TCheckbutton", variable=lock_mouse_var)
    lock_mouse.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    save_button = ttk.Button(root, text="Save & Exit", command=on_gui_close)
    save_button.grid(row=4, column=1, columnspan=2, pady=20, sticky="nsew")
    
    sv_ttk.use_dark_theme()

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

# Função para criar o ícone da bandeja
def create_tray_icon():
    global icon
    icon_image = create_icon()

    config = manage_config("load")

    def rebuild_menu():
        # Reconstrói o item com o texto atualizado
        toggle_item = MenuItem(
            "Unlock Mouse" if lock_mouse else "Lock Mouse",
            lambda icon, item: toggle_cursor_lock()
        )
        return Menu(
            toggle_item,
            MenuItem('Settings', settings_gui),
            MenuItem('Close', quit_program)
        )

    def toggle_cursor_lock():
        global lock_mouse
        lock_mouse = not lock_mouse
        set_cursorlock()
        manage_config("save", {"lock_mouse": lock_mouse})
        icon.menu = rebuild_menu()  # atualiza o menu

    icon = Icon("WindowMonitor", icon_image, menu=rebuild_menu())
    
    if config:
        print("Configuração encontrada! Iniciando monitoramento...")
        monitors, _, _ = get_monitors_info()
        target_monitor = monitors.get(TARGET_MONITOR_KEY, None)
        if target_monitor is None:
            print(f"Erro: Monitor alvo '{TARGET_MONITOR_KEY}' não encontrado!")
        else:
            print("Movendo janela para o monitor:")
            start_correction_thread(WINDOW_CLASS, target_monitor)
    else:
        print("Nenhuma configuração encontrada. Abrindo configurações...")
        settings_gui()
    icon.run()

# Função para encerrar o programa
def quit_program(icon, item):
    global monitor_thread
    print("Encerrando o programa...")
    stop_correction_thread()  # Sinaliza para a thread parar
    
    # Envia mensagem para encerrar o loop PumpMessages
    if monitor_thread and monitor_thread.is_alive():
        print("Encerrando monitoramento de eventos do Windows...")
        win32gui.PostQuitMessage(0)
    try:
        if root and root.winfo_exists():  # Verifica se a janela ainda está aberta
            root.destroy()
    except Exception as e:
        print(f"Erro ao destruir a janela: {e}")
        
    icon.stop()  # Para o ícone da bandeja corretamente
    print("Programa encerrado.")

# Função chamada ao fechar a janela de configurações
def on_gui_close():
    global stop_thread, root
    
    manage_config("update")
    manage_config("load")
      
    if correction_thread and correction_thread.is_alive(): # Mata thread e incia novamente com novas configurções
        stop_correction_thread()
        start_correction_thread(WINDOW_CLASS, TARGET_MONITOR_KEY)
    else:
        start_correction_thread(WINDOW_CLASS, TARGET_MONITOR_KEY)
    
    root.destroy()
    root = None




#Main function
def main():
    # Inicia a thread que escuta eventos do Windows
    monitor_thread = threading.Thread(target=lambda: WindowMonitorHook().register_window(), daemon=True)
    monitor_thread.start()

    # Criação do ícone da bandeja e monitoramento
    create_tray_icon()

if __name__ == "__main__":
    main()
