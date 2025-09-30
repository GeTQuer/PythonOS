import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, Label
import shlex
import os
import argparse
import time
import csv
import base64

# --------------------------
# Простая VFS (словарь)
# --------------------------
VFS = {"/": {}}        # дерево каталогов/файлов
CURRENT_DIR = ["/"]    # список частей пути (корень = ["/"])

def norm_path(path):
    if not path:
        return CURRENT_DIR[:]
    if path.startswith("/"):
        parts = ["/"]
        tail = path.strip("/").split("/")
    else:
        parts = CURRENT_DIR[:]
        tail = path.split("/")
    for p in tail:
        if p in ("", "."):
            continue
        if p == "..":
            if len(parts) > 1:
                parts.pop()
        else:
            parts.append(p)
    return parts

def get_node(parts):
    """Возвращает узел по списку частей пути"""
    node = VFS["/"]
    for p in parts[1:]:
        if not isinstance(node, dict):
            return None
        node = node.get(p)
        if node is None:
            return None
        if isinstance(node, dict) and "type" in node and node["type"] == "file":
            return None
    return node

def load_vfs(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"VFS CSV файл '{csv_path}' не найден")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            path = row["path"]
            typ = row["type"]
            enc = row["encoding"]
            cont = row["content"]

            parts = norm_path(path)
            fname = parts[-1]
            parent = get_node(parts[:-1])
            if parent is None:
                # создаём промежуточные каталоги
                parent = VFS["/"]
                for p in parts[1:-1]:
                    parent = parent.setdefault(p, {})

            if typ == "dir":
                parent[fname] = {}
            elif typ == "file":
                if enc == "base64":
                    data = base64.b64decode(cont.encode("ascii"))
                else:
                    data = cont
                parent[fname] = {"type": "file", "encoding": enc, "content": data}

def ls(path=None):
    parts = norm_path(path) if path else CURRENT_DIR
    node = get_node(parts)
    if node is None or not isinstance(node, dict):
        return ["Ошибка: не директория"]
    return list(node.keys())

def cd(path):
    global CURRENT_DIR
    parts = norm_path(path)
    node = get_node(parts)
    if node is None or not isinstance(node, dict):
        return f"Ошибка: нет такой директории '{path}'"
    CURRENT_DIR = parts
    return f"Текущая директория: {'/'.join(CURRENT_DIR) if CURRENT_DIR != ['/'] else '/'}"

# --------------------------
# GUI часть (твоя)
# --------------------------
def main():
    parser = argparse.ArgumentParser(description='VFS Terminal Emulator')
    parser.add_argument('--vfs-csv', required=True, help="Путь к CSV файлу с виртуальной ФС")
    args = parser.parse_args()

    # загружаем VFS
    try:
        load_vfs(args.vfs_csv)
    except Exception as e:
        print(f"Ошибка загрузки VFS: {e}")
        return

    root = tk.Tk()
    root.title("VFS Terminal Emulator")
    root.geometry("800x600")

    main_frame = Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    output_area = scrolledtext.ScrolledText(
        main_frame,
        wrap=tk.WORD,
        bg='black',
        fg='green',
        insertbackground='white',
        font=('Courier New', 10)
    )
    output_area.pack(fill=tk.BOTH, expand=True)
    output_area.config(state=tk.DISABLED)

    input_frame = Frame(main_frame, bg='black')
    input_frame.pack(fill=tk.X, pady=(5, 0))

    prompt_label = Label(
        input_frame,
        text="user@vfs:/ $ ",
        bg='black',
        fg='green',
        font=('Courier New', 10)
    )
    prompt_label.pack(side=tk.LEFT)
    entry = Entry(
        input_frame,
        bg='black',
        fg='white',
        insertbackground='white',
        font=('Courier New', 10),
        width=50
    )
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    entry.focus()

    def output(text):
        output_area.config(state=tk.NORMAL)
        output_area.insert(tk.END, text + '\n')
        output_area.config(state=tk.DISABLED)
        output_area.see(tk.END)

    def show_prompt():
        cwd_str = "/" if CURRENT_DIR == ["/"] else "/".join(CURRENT_DIR)
        prompt_label.config(text=f"user@vfs:{cwd_str}$ ")

    def exit_command():
        output("Выход из VFS Terminal Emulator...")
        root.after(2000, root.destroy)

    def ls_command(args):
        items = ls(args[0] if args else None)
        for it in items:
            output(it)

    def cd_command(args):
        if not args:
            return
        res = cd(args[0])
        output(res)

    def clear_command():
        output_area.config(state=tk.NORMAL)
        output_area.delete(1.0, tk.END)
        output_area.config(state=tk.DISABLED)

    def parse_command(command_text):
        try:
            parts = shlex.split(command_text)
            if not parts:
                return None, []
            return parts[0].lower(), parts[1:]
        except ValueError as e:
            return "parse_error", [str(e)]

    def process_command(event=None, command_text=None):
        if command_text is None:
            command_text = entry.get().strip()
            entry.delete(0, tk.END)

        cwd_str = "/" if CURRENT_DIR == ["/"] else "/".join(CURRENT_DIR)
        output(f"user@vfs:{cwd_str}$ {command_text}")

        if not command_text or command_text.startswith('#'):
            show_prompt()
            return

        command, args = parse_command(command_text)

        handlers = {
            "exit": exit_command,
            "ls": lambda: ls_command(args),
            "cd": lambda: cd_command(args),
            "clear": clear_command,
        }

        if command in handlers:
            handlers[command]()
        else:
            output(f"Команда '{command}' не найдена")

        show_prompt()

    entry.bind('<Return>', process_command)

    output("Добро пожаловать в VFS Terminal Emulator")
    output("Введите 'exit' для выхода")
    output("Доступные команды: ls, cd, clear")
    show_prompt()

    root.mainloop()

if __name__ == "__main__":
    main()
