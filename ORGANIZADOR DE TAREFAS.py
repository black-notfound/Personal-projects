import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, DANGER, PRIMARY, WARNING, INFO
from tkcalendar import Calendar as BaseCalendar
class Calendar(BaseCalendar):
    def __init__(self, *args, **kwargs):
        # 1) inicializa self._properties com style como key
        #    para que configure(style=...) não exploda
        self._properties = {"style": None}
        super().__init__(*args, **kwargs)
import datetime
import threading
import time
import json
import os

# Arquivos
TASKS_FILE = "tasks.json"
ROUTINE_FILE = "routine.json"

# Primeiro dia de trabalho
START_WORK_DATE = datetime.date(2025, 1, 1)

# Funções de Tarefas
def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def load_routine():
    if os.path.exists(ROUTINE_FILE):
        with open(ROUTINE_FILE, "r") as f:
            return json.load(f)
    return [
        {"task": "30 min de Exercício", "duration": 30},
        {"task": "2h Estudo de Python", "duration": 120},
    ]

def save_routine(routine):
    with open(ROUTINE_FILE, "w") as f:
        json.dump(routine, f, indent=4)

# Funções de Rotina
def on_date_select(event):
    selected_date = cal.get_date()
    show_tasks(selected_date)

def show_tasks(date):
    tasks_list.delete(0, tk.END)
    tasks = tasks_data.get(date, [])
    for task in tasks:
        tasks_list.insert(tk.END, task)

def add_task():
    selected_date = cal.get_date()
    task = simpledialog.askstring("Adicionar tarefa", "Descreva a tarefa:")
    if task:
        tasks_data.setdefault(selected_date, []).append(task)
        save_tasks(tasks_data)
        show_tasks(selected_date)

def remove_task():
    selected_date = cal.get_date()
    selected_index = tasks_list.curselection()
    if selected_index:
        task = tasks_list.get(selected_index)
        tasks_data[selected_date].remove(task)
        save_tasks(tasks_data)
        show_tasks(selected_date)

def highlight_work_days():
    cal.calevent_remove('all')
    year = cal.selection_get().year
    month = cal.selection_get().month
    first_day = datetime.date(year, month, 1)
    last_day = datetime.date(year, month+1, 1) - datetime.timedelta(days=1) if month < 12 else datetime.date(year+1, 1, 1) - datetime.timedelta(days=1)

    current_day = START_WORK_DATE
    work_today = True
    while current_day <= last_day:
        if current_day >= first_day:
            if work_today:
                cal.calevent_create(current_day, 'Trabalho', 'work')
            else:
                cal.calevent_create(current_day, 'Folga', 'off')
        current_day += datetime.timedelta(days=1)
        work_today = not work_today

    cal.tag_config('work', background='lightgreen')
    cal.tag_config('off', background='lightblue')

def generate_day_schedule():
    selected_date = datetime.datetime.strptime(cal.get_date(), "%Y-%m-%d").date()
    current_day = START_WORK_DATE
    work_today = True
    while current_day < selected_date:
        current_day += datetime.timedelta(days=1)
        work_today = not work_today

    if work_today:
        messagebox.showwarning("Dia de Trabalho", "Hoje é dia de trabalho! Rotina não gerada.")
        return

    start_time = simpledialog.askstring("Início do Dia", "Hora inicial? (formato HH:MM)", initialvalue="08:00")
    if not start_time:
        return

    try:
        current_time = datetime.datetime.strptime(start_time, "%H:%M")
    except ValueError:
        messagebox.showerror("Erro", "Formato inválido. Use HH:MM.")
        return

    generated_tasks = []
    for item in routine:
        time_str = current_time.strftime("%H:%M")
        generated_tasks.append(f"{time_str} - {item['task']}")
        current_time += datetime.timedelta(minutes=item['duration'])

    tasks_data[selected_date.strftime("%Y-%m-%d")] = generated_tasks
    save_tasks(tasks_data)
    show_tasks(selected_date.strftime("%Y-%m-%d"))
    messagebox.showinfo("Sucesso", "Rotina do dia criada!")

def manage_routines():
    routine_window = ttk.Toplevel(root)
    routine_window.title("Gerenciar Rotinas")

    listbox = tk.Listbox(routine_window, width=50)
    listbox.pack(pady=10)

    for item in routine:
        listbox.insert(tk.END, f"{item['task']} ({item['duration']} min)")

    def edit_selected():
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            new_task = simpledialog.askstring("Editar Tarefa", "Nova descrição:", initialvalue=routine[index]['task'])
            new_duration = simpledialog.askinteger("Editar Duração", "Nova duração (minutos):", initialvalue=routine[index]['duration'])
            if new_task and new_duration:
                routine[index] = {"task": new_task, "duration": new_duration}
                save_routine(routine)
                routine_window.destroy()
                manage_routines()

    def delete_selected():
        selected = listbox.curselection()
        if selected:
            index = selected[0]
            confirm = messagebox.askyesno("Excluir", "Deseja excluir esta rotina?")
            if confirm:
                routine.pop(index)
                save_routine(routine)
                routine_window.destroy()
                manage_routines()

    btn_frame = ttk.Frame(routine_window)
    btn_frame.pack(pady=5)

    edit_btn = ttk.Button(btn_frame, text="Editar", command=edit_selected, bootstyle=INFO)
    edit_btn.grid(row=0, column=0, padx=5)

    delete_btn = ttk.Button(btn_frame, text="Excluir", command=delete_selected, bootstyle=DANGER)
    delete_btn.grid(row=0, column=1, padx=5)

def check_tasks():
    while True:
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        if today in tasks_data:
            for task in tasks_data[today]:
                time_part, desc = task.split(' - ', 1)
                task_time = datetime.datetime.strptime(time_part, "%H:%M").time()
                if task_time.hour == now.hour and task_time.minute == now.minute:
                    messagebox.showinfo("Hora da Tarefa!", f"Agora: {desc}")
                    time.sleep(60)
        time.sleep(30)

# Interface
root = ttk.Window(themename="darkly")
cal = Calendar(
    root,
    selectmode="day",
    date_pattern="yyyy-mm-dd",

    # 👇 aqui já dá pra estilizar o calendário manualmente em dark theme:
    background='black',
    disabledbackground='gray20',
    foreground='white',
    disabledforeground='gray50',
    selectbackground='gray30',
    selectforeground='white',
    headersbackground='gray10',
    headersforeground='white',
    normalbackground='black',
    normalforeground='white',
    weekendbackground='black',
    weekendforeground='white',
)
cal.pack(pady=10)
root.title("Gerenciador de Rotina")
root.geometry("500x700")

tasks_data = load_tasks()
routine = load_routine()

# Não use ttkbootstrap aqui no calendário:
cal = Calendar(root, selectmode="day", date_pattern="yyyy-mm-dd")
cal.pack(pady=10)
cal.bind("<<CalendarSelected>>", on_date_select)
cal.bind("<<MonthChanged>>", lambda e: highlight_work_days())

tasks_list = tk.Listbox(root, width=50)
tasks_list.pack(pady=10)

buttons_frame = ttk.Frame(root)
buttons_frame.pack(pady=10)

add_button = ttk.Button(buttons_frame, text="Adicionar Tarefa", command=add_task, bootstyle=SUCCESS)
add_button.grid(row=0, column=0, padx=5)

remove_button = ttk.Button(buttons_frame, text="Remover Tarefa", command=remove_task, bootstyle=DANGER)
remove_button.grid(row=0, column=1, padx=5)

generate_button = ttk.Button(buttons_frame, text="Gerar Rotina do Dia", command=generate_day_schedule, bootstyle=PRIMARY)
generate_button.grid(row=1, column=0, padx=5, pady=5)

manage_routine_button = ttk.Button(buttons_frame, text="Gerenciar Rotinas", command=manage_routines, bootstyle=WARNING)
manage_routine_button.grid(row=1, column=1, padx=5, pady=5)

show_tasks(cal.get_date())
highlight_work_days()

task_checker_thread = threading.Thread(target=check_tasks, daemon=True)
task_checker_thread.start()

root.mainloop()
