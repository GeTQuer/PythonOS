import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, Label
import shlex
import os
import argparse
import time


def main():
    parser = argparse.ArgumentParser(description='VFS Terminal Emulator')
    parser.add_argument('--vfs-path')
    parser.add_argument('--startup-script')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    startup_script = None
    if args.startup_script:
        if not os.path.isabs(args.startup_script):
            startup_script = os.path.join(script_dir, args.startup_script)
        else:
            startup_script = args.startup_script
    vfs_path = os.path.join(os.path.dirname(startup_script),"main.py")
    print("=== VFS Terminal Startup Parameters ===")
    print(f"Script Directory: {script_dir}")
    print(f"VFS Path: {vfs_path}")
    print(f"Startup Script: {startup_script or 'Не указан'}")
    print("=======================================")

    root = tk.Tk()
    root.title("VFS Terminal Emulator")
    root.geometry("800x600")

    current_directory = "/home/user"
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
        text=f"user@vfs:{current_directory}$ ",
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
        prompt_label.config(text=f"user@vfs:{current_directory}$ ")

    def exit_command():
        output("Выход из VFS Terminal Emulator...")
        root.after(2000, root.destroy)

    def ls_command(args):
        nonlocal current_directory
        target_dir = current_directory
        if args:
            if args[0].startswith('/'):
                target_dir = args[0]
            else:
                target_dir = os.path.join(current_directory, args[0])
        output(f"Содержимое {target_dir}:")
        output("file1.txt")
        output("file2.txt")
        output("documents/")
        output("pictures/")

    def cd_command(args):
        nonlocal current_directory
        if not args:
            current_directory = "/home/user"
            output(f"Переход в домашнюю директорию: {current_directory}")
            return
        target_dir = args[0]
        if target_dir == "..":
            if current_directory != "/":
                current_directory = os.path.dirname(current_directory) or "/"
                output(f"Текущая директория: {current_directory}")
            else:
                output("Вы уже в корневой директории")
        elif target_dir.startswith('/'):
            current_directory = target_dir
            output(f"Переход в: {current_directory}")
        else:
            new_dir = os.path.join(current_directory, target_dir)
            current_directory = new_dir
            output(f"Переход в: {current_directory}")

    def clear_command():
        output_area.config(state=tk.NORMAL)
        output_area.delete(1.0, tk.END)
        output_area.config(state=tk.DISABLED)

    def parse_command(command_text):
        try:
            parts = shlex.split(command_text)
            if not parts:
                return None, []
            command = parts[0].lower()
            args = parts[1:]
            return command, args
        except ValueError as e:
            return "parse_error", [str(e)]

    def process_command(event=None, command_text=None):
        nonlocal current_directory
        if command_text is None:
            command_text = entry.get().strip()
            entry.delete(0, tk.END)

        output(f"user@vfs:{current_directory}$ {command_text}")

        if not command_text or command_text.startswith('#'):
            show_prompt()
            return

        command, args = parse_command(command_text)
        if command is None:
            show_prompt()
            return

        command_handlers = {
            "exit": exit_command,
            "ls": lambda: ls_command(args),
            "cd": lambda: cd_command(args),
            "clear": clear_command,
        }

        if command in command_handlers:
            command_handlers[command]()
        else:
            output(f"Команда '{command}' не найдена")

        show_prompt()

    def execute_startup_script(script_path):
        try:
            if not os.path.exists(script_path):
                output(f"Ошибка: файл скрипта '{script_path}' не найден")
                return

            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            output(f"=== Выполнение стартового скрипта: {script_path} ===")

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Пропускаем пустые строки и комментарии
                if not line or line.startswith('#'):
                    continue
                process_command(command_text=line)
                root.update()
                time.sleep(0.5)

            output("=== Выполнение скрипта завершено ===")

        except Exception as e:
            output(f"Ошибка выполнения скрипта: {str(e)}")

    entry.bind('<Return>', process_command)

    output("Добро пожаловать в VFS Terminal Emulator")
    output("Введите 'exit' для выхода")
    output("Доступные команды: ls, cd, clear")
    show_prompt()

    if startup_script:
        root.after(1000, lambda: execute_startup_script(startup_script))
    root.mainloop()


if __name__ == "__main__":
    main()