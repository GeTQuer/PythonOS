import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, Label
import shlex
import os


def main():
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
        root.after(1000, root.destroy)

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

    def process_command(event):
        nonlocal current_directory
        command_text = entry.get().strip()
        entry.delete(0, tk.END)

        output(f"user@vfs:{current_directory}$ {command_text}")
        command, args = parse_command(command_text)

        if command is None:
            show_prompt()
            return

        command_handlers = {
            "exit": exit_command,
            "ls": lambda: ls_command(args),
            "cd": lambda: cd_command(args),
            "<<clear>>": clear_command,
            "parse_error": lambda: output(f"Ошибка парсинга: {args[0]}")
        }

        if command in command_handlers:
            command_handlers[command]()
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