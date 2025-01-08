import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import json
import logging
import hashlib
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def load_config(config_path):
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Ошибка загрузки конфигурации: {e}")
        return {}
def save_config(config, config_path):
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logging.info("Конфигурация сохранена.")
    except Exception as e:
        logging.error(f"Ошибка сохранения конфигурации: {e}")
        messagebox.showerror("Ошибка", f"Не удалось сохранить конфигурацию: {e}")

def find_java_executable(config):
    java_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "java8-windows-64")
    java_exe = "javaw.exe"
    java_path = os.path.join(java_dir, "bin", java_exe)
    if os.path.exists(java_path) and os.access(java_path, os.X_OK):
        logging.info(f"Использую Java из папки java8-windows-64: {java_path}")
        return java_path
    java_exe = "java.exe" if os.name == 'nt' else "java"
    paths = os.environ.get("PATH", "").split(os.pathsep)
    for path in paths:
        full_path = os.path.join(path, java_exe)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path
    if os.name == "nt":
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            full_path = os.path.join(java_home, "bin", java_exe)
            if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                return full_path
    logging.error("Не удалось найти исполняемый файл Java.")
    return None
def get_game_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        'base': base_dir,
        'versions': os.path.join(base_dir, "versions"),
        'libraries': os.path.join(base_dir, "libraries"),
        'assets': os.path.join(base_dir, "assets"),
    }
def generate_offline_uuid(username):
    hashed_username = hashlib.md5(username.encode('utf-8')).hexdigest()
    uuid = f"{hashed_username[:8]}-{hashed_username[8:12]}-{hashed_username[12:16]}-{hashed_username[16:20]}-{hashed_username[20:32]}"
    return uuid
def get_version_info(paths):
    version_name = "1.12.2"
    version_dir = os.path.join(paths['versions'], version_name)
    if not os.path.exists(version_dir) or not os.path.isdir(version_dir):
        logging.error(f"Папка версии  не найдена: {version_dir}")
        messagebox.showerror("Ошибка", f"Папка версии {version_name} не найдена.")
        return None, None
    return version_dir, version_name
def check_version_files(version_dir, version_name):
    version_jar = os.path.join(version_dir, f"{version_name}.jar")
    version_json = os.path.join(version_dir, f"{version_name}.json")
    if not os.path.exists(version_jar):
        logging.error(f"Файл .jar не найден в {version_dir}")
        messagebox.showerror("Ошибка", f"Файл {version_name}.jar не найден.")
        return None, None
    if not os.path.exists(version_json):
        logging.error(f"Файл .json не найден в {version_dir}")
        messagebox.showerror("Ошибка", f"Файл {version_name}.json не найден.")
        return None, None
    return version_jar, version_json
def find_natives(version_dir):
    natives_path = os.path.join(version_dir, "natives")
    if not os.path.exists(natives_path):
        logging.error(f"Не найдена папка natives в {version_dir}")
        messagebox.showerror("Ошибка", f"Не найдена папка natives в {version_dir}")
        return None
    logging.info(f"Найдена папка natives: {natives_path}")
    return natives_path
def create_launch_command(config, paths, version_dir, version_name, username, version_jar, natives_path, assetIndex, uuid):
    lib_path = os.path.join(paths['libraries'], "*")
    if not os.path.exists(paths['libraries']):
        logging.error("Папка 'libraries' не найдена.")
        messagebox.showerror("Ошибка", "Папка 'libraries' не найдена.")
        return None
    command = [
        config.get("java_path"),
        "-Xmx" + config.get("max_memory", "2G"),
        "-Djava.library.path=" + natives_path,
        "-cp",
        f';;'
        f'{version_jar};'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\turikhay\\ca-fixer\\1.0\\ca-fixer-1.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\optifine\\OptiFine\\1.12.2_HD_U_G5\\OptiFine-1.12.2_HD_U_G5.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\optifine\\launchwrapper\\2.2\\launchwrapper-2.2.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\ru\\tlauncher\\patchy\\1.0.0\\patchy-1.0.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\oshi-project\\oshi-core\\1.1\\oshi-core-1.1.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\net\\java\\dev\\jna\\jna\\4.4.0\\jna-4.4.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\net\\java\\dev\\jna\\platform\\3.4.0\\platform-3.4.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\ibm\\icu\\icu4j-core-mojang\\51.2\\icu4j-core-mojang-51.2.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\net\\sf\\jopt-simple\\jopt-simple\\5.0.3\\jopt-simple-5.0.3.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\paulscode\\codecjorbis\\20101023\\codecjorbis-20101023.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\paulscode\\codecwav\\20101023\\codecwav-20101023.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\paulscode\\libraryjavasound\\20101123\\libraryjavasound-20101123.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\paulscode\\librarylwjglopenal\\20100824\\librarylwjglopenal-20100824.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\paulscode\\soundsystem\\20120107\\soundsystem-20120107.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\io\\netty\\netty-all\\4.1.9.Final\\netty-all-4.1.9.Final.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\google\\guava\\guava\\21.0\\guava-21.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\google\\code\\gson\\gson\\2.8.0\\gson-2.8.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\org\\apache\\commons\\commons-lang3\\3.5\\commons-lang3-3.5.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\commons-io\\commons-io\\2.5\\commons-io-2.5.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\commons-codec\\commons-codec\\1.10\\commons-codec-1.10.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\net\\java\\jinput\\jinput\\2.0.5\\jinput-2.0.5.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\net\\java\\jutils\\jutils\\1.0.0\\jutils-1.0.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\google\\code\\gson\\gson\\2.8.0\\gson-2.8.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\by\\ely\\authlib\\3.11.49.2\\authlib-3.11.49.2.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\mojang\\realms\\1.10.22\\realms-1.10.22.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\org\\apache\\commons\\commons-compress\\1.8.1\\commons-compress-1.8.1.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\org\\apache\\httpcomponents\\httpclient\\4.3.3\\httpclient-4.3.3.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\commons-logging\\commons-logging\\1.1.3\\commons-logging-1.1.3.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\org\\apache\\httpcomponents\\httpcore\\4.3.2\\httpcore-4.3.2.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\it\\unimi\\dsi\\fastutil\\7.1.0\\fastutil-7.1.0.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\org\\apache\\logging\\log4j\\log4j-api\\2.8.1\\log4j-api-2.8.1.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\org\\apache\\logging\\log4j\\log4j-core\\2.8.1\\log4j-core-2.8.1.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\org\\lwjgl\\lwjgl\\lwjgl\\2.9.4-nightly-20150209\\lwjgl-2.9.4-nightly-20150209.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\org\\lwjgl\\lwjgl\\lwjgl_util\\2.9.4-nightly-20150209\\lwjgl_util-2.9.4-nightly-20150209.jar;'
        f'C:\\Users\\sineg\\Desktop\\lp\\libraries\\com\\mojang\\text2speech\\1.10.3\\text2speech-1.10.3.jar;',
        config.get("main_class", "net.minecraft.client.main.Main"),
        "--version", "OptiFine 1.12.2",
        "--gameDir", paths['base'],
        "--assetsDir", paths['assets'],
        "--assetIndex", assetIndex,
        "--uuid", uuid,
        "--accessToken", "0",
        "--userProperties", "{}",
        "--username", username,
        "--userType", "legacy",
        "--versionType", "release"
    ]
    logging.info(f"Команда запуска: {' '.join(command)}")
    return command
def launch_minecraft(config, paths, username, root_window):
    try:
        uuid = generate_offline_uuid(username)
        version_dir, version_name = get_version_info(paths)
        if not version_dir or not version_name:
            return
        version_jar, version_json = check_version_files(version_dir, version_name)
        if not version_jar or not version_json:
            return
        assetIndex = "1.12.2"
        try:
            with open(version_json, 'r') as f:
                version_data = json.load(f)
                assetIndex = version_data.get("assets", "1.12.2") 
        except Exception as e:
            logging.warning(f"Не удалось загрузить assetIndex из json, устанавливаю в '1.12.2': {e}")
        natives_path = find_natives(version_dir)
        if natives_path is None:
            return
        
        command = create_launch_command(config, paths, version_dir, version_name, username, version_jar, natives_path, assetIndex, uuid)
        if command is None:
            return
        subprocess.Popen(command, cwd=paths['base'])
        logging.info("Minecraft запущен!")
        root_window.destroy() 
    except Exception as e:
        logging.exception(f"Произошла ошибка при запуске Minecraft: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить Minecraft: {e}")
def open_settings_window(config, root):
    settings_window = tk.Toplevel(root)
    settings_window.title("Настройки")
    ram_label = tk.Label(settings_window, text="Макс. ОЗУ (МБ):")
    ram_label.pack(pady=5)
    ram_var = tk.IntVar(value=int(config.get("max_memory", "2G")[:-1]) * 1024 if config.get("max_memory", "2G").endswith("G") else int(config.get("max_memory", "2048")) )
    ram_scale = tk.Scale(settings_window, from_=512, to=8192, orient=tk.HORIZONTAL, variable=ram_var)
    ram_scale.pack(pady=5)
    def save_settings():
        config["max_memory"] = str(ram_var.get()) + "M" 
        save_config(config, 'config.json')
        settings_window.destroy()

    def close_settings():
        settings_window.destroy()
    save_button = tk.Button(settings_window, text="Сохранить", command=save_settings)
    save_button.pack(side=tk.LEFT, padx=10, pady=10)
    back_button = tk.Button(settings_window, text="Назад", command=close_settings)
    back_button.pack(side=tk.LEFT, padx=10, pady=10)
def open_nickname_manager(config, root, nickname_combobox):
    nickname_window = tk.Toplevel(root)
    nickname_window.title("Менеджер никнеймов")
    nicknames = config.get("nicknames", [])
    def update_nickname_list():
        for widget in nickname_list_frame.winfo_children():
            widget.destroy()
        for nickname in nicknames:
            nickname_label = tk.Label(nickname_list_frame, text=nickname)
            nickname_label.pack(side=tk.TOP, fill=tk.X)
            edit_button = tk.Button(nickname_list_frame, text="Изменить", command=lambda n=nickname: edit_nickname(n, nickname_combobox))
            edit_button.pack(side=tk.LEFT, padx=5)
            delete_button = tk.Button(nickname_list_frame, text="Удалить", command=lambda n=nickname: delete_nickname(n))
            delete_button.pack(side=tk.LEFT, padx=5)
    def add_nickname():
        new_nickname = simpledialog.askstring("Добавить никнейм", "Введите новый никнейм:")
        if new_nickname and new_nickname not in nicknames:
            nicknames.append(new_nickname)
            config["nicknames"] = nicknames
            save_config(config, 'config.json')
            update_nickname_list()
            update_nickname_combobox(config, nickname_combobox)
    def edit_nickname(nickname, nickname_combobox):
        new_nickname = simpledialog.askstring("Изменить никнейм", "Введите новый никнейм:", initialvalue=nickname)
        if new_nickname and new_nickname != nickname:
            index = nicknames.index(nickname)
            nicknames[index] = new_nickname
            config["nicknames"] = nicknames
            save_config(config, 'config.json')
            update_nickname_list()
            update_nickname_combobox(config, nickname_combobox)
            nickname_combobox.set(new_nickname)
    def delete_nickname(nickname):
        if messagebox.askyesno("Удалить никнейм", f"Вы уверены, что хотите удалить никнейм '{nickname}'?"):
            nicknames.remove(nickname)
            config["nicknames"] = nicknames
            save_config(config, 'config.json')
            update_nickname_list()
            update_nickname_combobox(config, nickname_combobox)

    nickname_list_frame = tk.Frame(nickname_window)
    nickname_list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    add_button = tk.Button(nickname_window, text="Добавить никнейм", command=add_nickname)
    add_button.pack(pady=5)

    update_nickname_list()
def update_nickname_combobox(config, nickname_combobox):
    nicknames = config.get("nicknames", [])
    if nicknames:
        nickname_combobox['values'] = nicknames
        nickname_combobox.config(state="readonly")
    else:
        nickname_combobox['values'] = ["Никнеймов нету"]
        nickname_combobox.config(state="disabled")
        nickname_combobox.set("Никнеймов нету")
def create_gui(config):
    root = tk.Tk()
    root.title("Minecraft Launcher")

    username_label = tk.Label(root, text="Имя пользователя:")
    username_label.pack(pady=5)
    
    nickname_combobox = ttk.Combobox(root)
    nickname_combobox.pack(pady=5)
    update_nickname_combobox(config, nickname_combobox)
    def on_play_button():
        username = nickname_combobox.get()
        if username == "Никнеймов нету" or not username:
            messagebox.showerror("Ошибка","Пожалуйста, добавьте или выберите имя пользователя.")
            return
        paths = get_game_paths()
        launch_minecraft(config, paths, username, root)

    launch_button = tk.Button(root, text="Играть", command=on_play_button)
    launch_button.pack(pady=10)
    
    settings_button = tk.Button(root, text="Настройки", command=lambda: open_settings_window(config, root))
    settings_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    nickname_button = tk.Button(root, text="Управление никнеймами", command=lambda: open_nickname_manager(config, root, nickname_combobox))
    nickname_button.pack(side=tk.LEFT, padx=10, pady=10)

    return root

def main():
    config_path = 'config.json'
    config = load_config(config_path)

    if not config.get("java_path"):
        java_path = find_java_executable(config)
        if java_path:
            config["java_path"] = java_path
        else:
            messagebox.showerror("Ошибка", "Не удалось найти исполняемый файл Java.")
            return
    root = create_gui(config)
    root.mainloop()
if __name__ == "__main__":
    main()