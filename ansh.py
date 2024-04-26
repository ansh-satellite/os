# Extended CPU Scheduling Simulator

import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import random

# Define the Process class
class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.priority = priority

# Define priority_entries as a global list
priority_entries = []

def round_robin(processes, time_quanta):
    t = 0
    gantt = []
    completed = {}
    waiting_times = {}
    turnaround_times = {}

    while processes:
        available = [p for p in processes if p.arrival_time <= t]

        if not available:
            gantt.append("Idle")
            t += 1
            continue
        else:
            process = available[0]
            gantt.append(f"P{process.pid}|")
            processes.remove(process)
            rem_burst = process.burst_time

            if rem_burst <= time_quanta:
                t += rem_burst
                ct = t
                pid = process.pid
                arrival_time = process.arrival_time
                burst_time = process.burst_time
                tt = ct - arrival_time
                wt = tt - burst_time
                completed[pid] = [ct, tt, wt]
                waiting_times[pid] = wt
                turnaround_times[pid] = tt
                continue
            else:
                t += time_quanta
                process.burst_time -= time_quanta
                processes.append(process)

    avg_waiting_time = sum(waiting_times.values()) / len(waiting_times)
    avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times)

    return avg_waiting_time, avg_turnaround_time, gantt

def srtf(processes):
    current_time = 0
    completed_processes = []
    total_waiting_time = 0
    total_turnaround_time = 0
    num_processes = len(processes)
    gantt_chart = ""
    while len(completed_processes) < num_processes:
        runnable_processes = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
        if len(runnable_processes) == 0:
            current_time += 1
            gantt_chart += "| "
            continue
        shortest_process = min(runnable_processes, key=lambda p: p.remaining_time)
        if shortest_process.remaining_time == shortest_process.burst_time:
            shortest_process.start_time = current_time
        shortest_process.remaining_time -= 1
        current_time += 1
        gantt_chart += f"P{shortest_process.pid} | "
        if shortest_process.remaining_time == 0:
            shortest_process.completion_time = current_time
            shortest_process.turnaround_time = shortest_process.completion_time - shortest_process.arrival_time
            shortest_process.waiting_time = shortest_process.turnaround_time - shortest_process.burst_time
            total_waiting_time += shortest_process.waiting_time
            total_turnaround_time += shortest_process.turnaround_time
            completed_processes.append(shortest_process)
    avg_waiting_time = total_waiting_time / num_processes
    avg_turnaround_time = total_turnaround_time / num_processes
    return avg_waiting_time, avg_turnaround_time, gantt_chart

def fcfs(processes):
    n = len(processes)
    processes.sort(key=lambda x: (x.arrival_time, x.pid))
    waiting_time = [0] * n
    turnaround_time = [0] * n
    table = []
    current_time = 0
    gantt_chart = ""
    for i in range(n):
        process = processes[i]
        if process.arrival_time == 0:
            start_time = current_time
            current_time += process.burst_time
            end_time = current_time
        else:
            start_time = max(current_time, process.arrival_time)
            current_time = start_time + process.burst_time
            end_time = current_time
        gantt_chart += f"P{process.pid} | "
        turnaround = end_time - process.arrival_time
        waiting = turnaround - process.burst_time
        table.append((process.pid, process.arrival_time, process.burst_time, waiting, turnaround))
    avg_waiting_time = sum(waiting for _, _, _, waiting, _ in table) / n
    avg_turnaround_time = sum(turnaround for _, _, _, _, turnaround in table) / n
    return table, avg_waiting_time, avg_turnaround_time, gantt_chart

def shortest_job_first(processes):
    processes.sort(key=lambda x: (x.arrival_time, x.burst_time, x.pid))
    n = len(processes)
    completion_time = [0] * n
    waiting_time = [0] * n
    turnaround_time = [0] * n
    executed = [False] * n
    total_time = 0
    completed = 0
    gantt_chart = ""
    while completed != n:
        next_process_index = -1
        min_burst = float('inf')
        for i in range(n):
            if not executed[i] and processes[i].arrival_time <= total_time:
                if processes[i].arrival_time == 0:
                    next_process_index = i
                    break
                elif processes[i].burst_time < min_burst:
                    min_burst = processes[i].burst_time
                    next_process_index = i
        if next_process_index == -1:
            total_time += 1
            gantt_chart += "| "
            continue
        process = processes[next_process_index]
        gantt_chart += f"P{process.pid} | "
        completion_time[next_process_index] = total_time + process.burst_time
        turnaround_time[next_process_index] = completion_time[next_process_index] - process.arrival_time
        waiting_time[next_process_index] = turnaround_time[next_process_index] - process.burst_time
        executed[next_process_index] = True
        total_time += process.burst_time
        completed += 1
    avg_waiting_time = sum(waiting_time) / n
    avg_turnaround_time = sum(turnaround_time) / n
    return completion_time, waiting_time, turnaround_time, gantt_chart

def non_preemptive_priority(processes):
    n = len(processes)
    processes.sort(key=lambda x: (x.arrival_time, x.priority, x.pid))
    waiting_time = [0] * n
    turnaround_time = [0] * n
    table = []
    current_time = 0
    gantt_chart = ""
    
    for i in range(n):
        process = processes[i]
        if process.arrival_time == 0:
            start_time = current_time
            current_time += process.burst_time
            end_time = current_time
        else:
            start_time = max(current_time, process.arrival_time)
            current_time = start_time + process.burst_time
            end_time = current_time
        gantt_chart += f"P{process.pid} | "
        turnaround = end_time - process.arrival_time
        waiting = turnaround - process.burst_time
        table.append((process.pid, process.arrival_time, process.burst_time, waiting, turnaround))
    
    avg_waiting_time = sum(waiting for _, _, _, waiting, _ in table) / n
    avg_turnaround_time = sum(turnaround for _, _, _, _, turnaround in table) / n
    return table, avg_waiting_time, avg_turnaround_time, gantt_chart

def priority_scheduling(processes):
    current_time = 0
    completed_processes = []
    total_waiting_time = 0
    total_turnaround_time = 0
    num_processes = len(processes)
    gantt_chart = ""
    while len(completed_processes) < num_processes:
        runnable_processes = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
        if len(runnable_processes) == 0:
            current_time += 1
            gantt_chart += "| "
            continue
        highest_priority_process = min(runnable_processes, key=lambda p: p.priority)
        if highest_priority_process.remaining_time == highest_priority_process.burst_time:
            highest_priority_process.start_time = current_time
        highest_priority_process.remaining_time -= 1
        current_time += 1
        gantt_chart += f"P{highest_priority_process.pid} | "
        if highest_priority_process.remaining_time == 0:
            highest_priority_process.completion_time = current_time
            highest_priority_process.turnaround_time = highest_priority_process.completion_time - highest_priority_process.arrival_time
            highest_priority_process.waiting_time = highest_priority_process.turnaround_time - highest_priority_process.burst_time
            total_waiting_time += highest_priority_process.waiting_time
            total_turnaround_time += highest_priority_process.turnaround_time
            completed_processes.append(highest_priority_process)
    avg_waiting_time = total_waiting_time / num_processes
    avg_turnaround_time = total_turnaround_time / num_processes
    return avg_waiting_time, avg_turnaround_time, gantt_chart

def display_results(processes, algorithm, time_quanta=None):
    global priority_entries  # Make priority_entries accessible inside this function
    if algorithm == "FCFS":
        table, avg_waiting_time, avg_turnaround_time, gantt_chart = fcfs(processes)
        results_text = f"Average Waiting Time: {avg_waiting_time:.2f}\n"
        results_text += f"Average Turnaround Time: {avg_turnaround_time:.2f}\n\n"
        results_text += "Gantt Chart:\n"
        results_text += gantt_chart
        results_label.config(text=results_text)
        
    elif algorithm == "SJF":
        completion_time, waiting_time, turnaround_time, gantt_chart = shortest_job_first(processes)
        avg_waiting_time = sum(waiting_time) / len(waiting_time)
        avg_turnaround_time = sum(turnaround_time) / len(turnaround_time)
        results_text = f"Average Waiting Time: {avg_waiting_time:.2f}\n"
        results_text += f"Average Turnaround Time: {avg_turnaround_time:.2f}\n\n"
        results_text += "Gantt Chart:\n"
        results_text += gantt_chart
        results_label.config(text=results_text)
        
    elif algorithm == "SRTF":
        avg_waiting_time, avg_turnaround_time, gantt_chart = srtf(processes)
        results_text = f"Average Waiting Time: {avg_waiting_time:.2f}\n"
        results_text += f"Average Turnaround Time: {avg_turnaround_time:.2f}\n\n"
        results_text += "Gantt Chart:\n"
        results_text += gantt_chart
        results_label.config(text=results_text)
        
    elif algorithm == "Round Robin":
        if time_quanta is None or time_quanta == "":
            results_label.config(text="Please enter a time quantum for Round Robin.")
            return
        else:
            try:
                time_quanta = int(time_quanta)
            except ValueError:
                results_label.config(text="Time quantum must be an integer.")
                return
            if time_quanta <= 0:
                results_label.config(text="Time quantum must be a positive integer.")
                return
            else:
                avg_waiting_time, avg_turnaround_time, gantt_chart = round_robin(processes, time_quanta)
                results_text = f"Average Waiting Time: {avg_waiting_time:.2f}\n"
                results_text += f"Average Turnaround Time: {avg_turnaround_time:.2f}\n\n"
                results_text += "Gantt Chart:\n"
                results_text += " ".join(gantt_chart)
                results_label.config(text=results_text)
                
    elif algorithm == "Non Preemptive Priority":
        for p, priority in zip(processes, priority_entries):
            p.priority = priority
        table, avg_waiting_time, avg_turnaround_time, gantt_chart = non_preemptive_priority(processes)
        results_text = f"Average Waiting Time: {avg_waiting_time:.2f}\n"
        results_text += f"Average Turnaround Time: {avg_turnaround_time:.2f}\n\n"
        results_text += "Note: Small values have high priority.\n"
        results_text += "Gantt Chart:\n"
        results_text += gantt_chart
        
        results_label.config(text=results_text)
       
        
    elif algorithm == "Preemptive Priority":  
        for p, priority in zip(processes, priority_entries):
            p.priority = int(priority)  # Remove .get() here
        avg_waiting_time, avg_turnaround_time, gantt_chart = priority_scheduling(processes)
        results_text = f"Average Waiting Time: {avg_waiting_time:.2f}\n"
        results_text += f"Average Turnaround Time: {avg_turnaround_time:.2f}\n\n"
        results_text += "Note: Small values have high priority.\n"
        results_text += "Gantt Chart:\n"
        results_text += gantt_chart
       
        results_label.config(text=results_text)
        
        
    else:
        results_label.config(text="Invalid algorithm selected.")
        
def display_table(table):
    table_window = tk.Toplevel(root)
    table_window.title("Schedule Table")
    table_frame = ttk.Frame(table_window)
    table_frame.pack(padx=20, pady=20)
    headers = ["Process ID", "Arrival Time", "Burst Time", "Waiting Time", "Turnaround Time"]
    for i, header in enumerate(headers):
        ttk.Label(table_frame, text=header, font=("Arial", 10, "bold")).grid(row=0, column=i, padx=5, pady=5)
    for i, row in enumerate(table, start=1):
        for j, value in enumerate(row):
            ttk.Label(table_frame, text=value, font=("Arial", 10)).grid(row=i, column=j, padx=5, pady=5)
            
def add_process_from_file():
    # Function to add processes from a file
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r') as file:
            for line in file:
                pid, arrival_time, burst_time, priority = map(int, line.strip().split())
                processes.append(Process(pid, arrival_time, burst_time, priority))
            update_process_listbox()


def add_process():
    pid = len(processes) + 1
    arrival_time = int(arrival_entry.get())
    burst_time = int(burst_entry.get())
    priority = None
    if algorithm_combobox.get() == "Preemptive Priority" or algorithm_combobox.get() == "Non Preemptive Priority":
        priority = priority_entry.get()
        priority_entries.append(priority)  # Append priority entry to the list
    processes.append(Process(pid, arrival_time, burst_time, priority))
    update_process_listbox()

def remove_process():
    selected_index = process_listbox.focus()
    if selected_index:
        item = process_listbox.item(selected_index)
        pid = int(item["values"][0])
        for process in processes:
            if process.pid == pid:
                processes.remove(process)
                update_process_listbox()
                return


def update_process_listbox():
    process_listbox.delete(*process_listbox.get_children())
    for process in processes:
        process_listbox.insert("", "end", values=(process.pid, process.arrival_time, process.burst_time, process.priority))

def clear_processes():
    global processes
    processes = []
    update_process_listbox()

def get_algorithm():
    selected_algorithm = algorithm_combobox.get()
    if selected_algorithm == "Round Robin":
        time_quanta_label.grid(row=3, column=0, padx=5, pady=5)
        time_quanta_entry.grid(row=3, column=1, padx=5, pady=5)
        priority_label.grid_forget()
        priority_entry.grid_forget()
    elif selected_algorithm == "Non Preemptive Priority" or selected_algorithm == "Preemptive Priority":
        priority_label.grid(row=3, column=0, padx=5, pady=5)
        priority_entry.grid(row=3, column=1, padx=5, pady=5)
        time_quanta_label.grid_forget()
        time_quanta_entry.grid_forget()
    else:
        time_quanta_label.grid_forget()
        time_quanta_entry.grid_forget()
        priority_label.grid_forget()
        priority_entry.grid_forget()

def simulate():
    global priority_entries  # Declare priority_entries as global
    
    if len(processes) > 10:
        results_label.config(text="Only 10 processes are allowed.")
        return
    
    selected_algorithm = algorithm_combobox.get()
    if not processes:
        results_label.config(text="Please add processes.")
        return
    if selected_algorithm == "Round Robin" and (not time_quanta_entry.get().isdigit() or int(time_quanta_entry.get()) <= 0):
        results_label.config(text="Please enter a valid time quantum for Round Robin.")
        return
    
    display_results(processes, selected_algorithm, time_quanta_entry.get())

root = tk.Tk()
root.title("CPU Scheduling Simulator")
root.geometry("800x600")
bg_image = Image.open(r"C:/Users/Mehul/OneDrive/Desktop/practice/9dbcd4_solid_color_background_icolorpalette.png")
bg_image = bg_image.resize((800, 600), Image.ANTIALIAS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
bg_label.image = bg_photo  # Keep a reference to avoid garbage collection

# Initialize variables
processes = []
priority_entries = []  # Initialize priority_entries list

# Create widgets
algorithm_label = ttk.Label(root, text="Select scheduling algorithm:")
algorithm_label.grid(row=0, column=0, padx=5, pady=5)

algorithms = ["FCFS", "SJF", "SRTF", "Round Robin", "Non Preemptive Priority", "Preemptive Priority"]
algorithm_combobox = ttk.Combobox(root, values=algorithms)
algorithm_combobox.grid(row=0, column=1, padx=5, pady=5)
algorithm_combobox.bind("<<ComboboxSelected>>", lambda event: get_algorithm())

time_quanta_label = ttk.Label(root, text="Enter time quantum:")
time_quanta_entry = ttk.Entry(root)

priority_label = ttk.Label(root, text="Enter priority:")
priority_entry = ttk.Entry(root)

arrival_label = ttk.Label(root, text="Enter arrival time:")
arrival_label.grid(row=1, column=0, padx=5, pady=5)
arrival_entry = ttk.Entry(root)
arrival_entry.grid(row=1, column=1, padx=5, pady=5)

burst_label = ttk.Label(root, text="Enter burst time:")
burst_label.grid(row=2, column=0, padx=5, pady=5)
burst_entry = ttk.Entry(root)
burst_entry.grid(row=2, column=1, padx=5, pady=5)

add_button = ttk.Button(root, text="Add Process", command=add_process)
add_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

remove_button = ttk.Button(root, text="Remove Process", command=remove_process)
remove_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

clear_button = ttk.Button(root, text="Clear Processes", command=clear_processes)
clear_button.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

process_listbox = ttk.Treeview(root, columns=("PID", "Arrival Time", "Burst Time", "Priority"), show="headings")
process_listbox.heading("PID", text="PID")
process_listbox.heading("Arrival Time", text="Arrival Time")
process_listbox.heading("Burst Time", text="Burst Time")
process_listbox.heading("Priority", text="Priority")
process_listbox.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

add_file_button = ttk.Button(root, text="Add from File", command=add_process_from_file)
add_file_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

results_label = ttk.Label(root, text="", font=("Arial", 10))
results_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

simulate_button = ttk.Button(root, text="Simulate", command=simulate)
simulate_button.grid(row=6, column=1, padx=5, pady=5, sticky="ew")


get_algorithm()


root.mainloop()
