import os

import customtkinter
import ttkbootstrap as tb
from tkinter import *
from ttkbootstrap.constants import *
from customtkinter import *
from CTkListbox import *
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import simpledialog
import sqlite3
import threading
import time
import win32print
import win32ui
import win32con
from datetime import datetime
import customtkinter as ctk



from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Initialize counter
printer_name = "80mm Series Printer"  # Change this to your actual printer name

# 80mm paper size at 203 DPI (576px width)
PAPER_WIDTH = 576
LINE_HEIGHT = 50  # Increase for proper spacing
# Initialize the Tkinter window
# root = tk.Tk()
root = customtkinter.CTk(fg_color="#4cae61")
root.title("Sistem Poliklinike")
root.geometry("900x600")


# Initialize global variables
current_user = None
counter = 1  # Starting queue number
selected_department = None

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('system.db')
    c = conn.cursor()

    # Create user table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT,
                    role TEXT)''')

    # Create department table
    c.execute('''CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    number INTEGER)''')

    conn.commit()
    conn.close()


def create_user(username, password, role):
    """Creates a new user in the system."""
    conn = sqlite3.connect('system.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()


def check_user_credentials(username, password):
    """Check if the user credentials are correct."""
    conn = sqlite3.connect('system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user


def login():
    """Handle user login."""
    username = simpledialog.askstring("Login", "Emri:", parent=root,)
    password = simpledialog.askstring("Login", "Password:", parent=root, show='*')

    if not username or not password:
        messagebox.showwarning("Error!", "Ju lutem vendosni te dyja , emer dhe password")
        return

    user = check_user_credentials(username, password)
    if user:
        global current_user
        current_user = user
        # messagebox.showinfo("Login Successful", f"Welcome, {user[1]}!")
        show_dashboard()
    else:
        messagebox.showerror("Lidhja deshtoi!", "Emer dhe Password i pasakte!")


def logout():
    """Handle user logout."""
    global current_user
    current_user = None
    root.deiconify()  # Show the login screen
    login_screen()


def show_dashboard():
    """Show the main dashboard after login."""
    for widget in root.winfo_children():
        widget.destroy()

    # Show dashboard content
    if current_user[3] == "admin":
        create_admin_dashboard()
    else:
        create_user_dashboard()


def create_admin_dashboard():
    """Create the admin dashboard."""
    label = CTkLabel(root, text="Nderfaqja Admin", font=("Arial", 24, "bold"),
                     width=150, height=100,
                     text_color='#1b4b39',
                     )
    label.pack(pady=20)

    # Add Department button
    add_dept_button = CTkButton(root, text="Shto Departament", font=("Arial", 16), command=add_department,
                                width=100, height=80,
                                corner_radius=32, fg_color="#256818", hover_color="#4e933e",
                                border_color="#71a866", border_width=3, hover=True,
                                )
    add_dept_button.pack(pady=10)

    # Remove Department button
    remove_dept_button = CTkButton(root, text="Fshi Departament", font=("Arial", 16), command=remove_department,
                                   width=100, height=80,
                                   corner_radius=32, fg_color="#256818", hover_color="#4e933e",
                                   border_color="#71a866", border_width=3, hover=True,
                                   )
    remove_dept_button.pack(pady=10)

    # List departments
    list_depts_button = CTkButton(root, text="Listo Departamentet", font=("Arial", 16), command=list_departments,
                                  width=100, height=80,
                                  corner_radius=32, fg_color="#256818", hover_color="#4e933e",
                                  border_color="#71a866", border_width=3, hover=True,
                                  )
    list_depts_button.pack(pady=10)

    # Logout button
    logout_button = CTkButton(root, text="Dil", font=("Arial", 16), command=logout,
                              width=100, height=80,
                              corner_radius=32, fg_color="#256818", hover_color="#4e933e",
                              border_color="#71a866", border_width=3, hover=True,
                              )
    logout_button.pack(pady=20)


def create_user_dashboard():
    """Create the user dashboard."""

    label = CTkLabel(root, text="Zgjidhni nje nga sherbimet", width=600, height=100,font=("Arial", 30, "bold"),
        bg_color="#4cae61",corner_radius=10, text_color="#0e3710", pady=20)
    label.pack(pady=30)

    # Show the list of departments
    show_departments_button = CTkButton(root, text="Shfaq Departamentet", font=("Arial", 24), command=show_departments,
                            corner_radius=32, fg_color="#2c9531", hover_color="#41d048",
                             border_color="#59d5a6", border_width=3,
                             width=150, height=100, text_color="white",)
    show_departments_button.pack(pady=10)

    # Logout button
    logout_button = CTkButton(root, text="Dil", font=("Arial", 24), command=logout,
                              corner_radius=32, fg_color="#235f48", hover_color="#3c9271",
                             border_color="#59d5a6", border_width=3,
                             width=150, height=100, text_color="white",)
    logout_button.pack(pady=20)


def show_value(selected_option):
    """Handle the selected option."""
    print(selected_option)



def show_departments():
    """Shfaq listën e departamenteve brenda dritares ekzistuese."""
    print("Hapja e departamenteve...")  # Për debug

    # Pastro dritaren ekzistuese
    for widget in root.winfo_children():
        widget.destroy()

    # Connecting to the database and fetching department data
    conn = sqlite3.connect('system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM departments")
    departments = c.fetchall()
    conn.close()

    # Creating the label for department selection
    dept_label = ctk.CTkLabel(root, text="Zgjidh një departament:", font=("Arial", 20),
                              bg_color="#4cae61", corner_radius=10, text_color="#0e3710", pady=20)
    dept_label.pack(pady=10)

    dept_var = tk.StringVar()

    # Create a Frame to hold the Listbox and Scrollbar together
    listbox_frame = tk.Frame(root)
    listbox_frame.pack(pady=10)

    # Create a Listbox widget to display department names
    dept_listbox = tk.Listbox(listbox_frame, height=10, width=30, font=("Arial", 18), selectmode=tk.SINGLE, bg="#77cead")
    for dept in departments:
        dept_listbox.insert(tk.END, dept[1])  # Add department name to the listbox
    dept_listbox.pack(side="left", fill="both", expand=True)

    # Create a Scrollbar widget and attach it to the Listbox
    scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=dept_listbox.yview)
    scrollbar.pack(side="right", fill="y")

    # Link the scrollbar with the listbox
    dept_listbox.config(yscrollcommand=scrollbar.set)

    # Function to handle selection event
    def on_select(event):
        selected_idx = dept_listbox.curselection()
        if selected_idx:
            selected_value = dept_listbox.get(selected_idx[0])
            show_value(selected_value)  # Call show_value when an option is selected

    # Bind the listbox to call the show_value function on selection
    dept_listbox.bind("<<ListboxSelect>>", on_select)

    def select_department():
        selected_dept_idx = dept_listbox.curselection()
        if selected_dept_idx:
            department_name = dept_listbox.get(selected_dept_idx[0])
            global selected_department
            selected_department = department_name
            show_queue(department_name)  # Shfaq radhën e departamentit të zgjedhur
        else:
            messagebox.showwarning("Gabim në zgjedhje", "Ju lutem zgjidhni një departament.")

    # Button to select a department
    select_button = ctk.CTkButton(root, text="Shiko radhën...", font=("Arial", 18), command=select_department,
                                  width=250, height=100,
                                  corner_radius=32, fg_color="#164384", hover_color="#608ac6",
                                  border_color="#1c5373", border_width=3, hover=True,
                                  )
    select_button.pack(pady=10)

    # Go back button
    def go_back():
        show_dashboard()

    back_button = ctk.CTkButton(root, text="Kthehu", font=("Arial", 18), command=go_back,
                                width=250, height=100,
                                corner_radius=32, fg_color="#164384", hover_color="#608ac6",
                                border_color="#1c5373", border_width=3, hover=True,
                                )
    back_button.pack(pady=10)



department_counters = {}


def show_queue(department_name):
    """Shfaq informacionin e departamentit të zgjedhur në të njëjtën dritare."""
    # Pastro dritaren ekzistuese
    for widget in root.winfo_children():
        widget.destroy()

    if department_name not in department_counters:
        department_counters[department_name] = 1

    # Trego radhën aktuale për departamentin
    queue_label = CTkLabel(root, text=f"Rradha aktuale në {department_name} është: {department_counters[department_name]}",
                           font=("Arial", 18),bg_color="#4cae61",corner_radius=10, text_color="#0e3710", pady=20 )
    queue_label.pack(pady=10)

    def increment_counter():
        """Increment the counter and print the receipt directly."""
        department_counters[department_name] += 1  # Increment the counter for the specific department
        queue_label.configure(text=f"Rradha aktuale në {department_name} është: {department_counters[department_name]}")  # Update the label with the new counter value
        print(f"Current queue for {department_name}: {department_counters[department_name]}")

    def reset_counter():
        """Reset the counter every 24 hours."""
        global department_counters
        while True:
            time.sleep(86400)  # Wait for 24 hours (86,400 seconds)
            department_counters = {key: 1 for key in department_counters}  # Reset all department counters
            print("Counters reset")

    # Butoni për të printuar biletën
    def print_receipt(number):
        """Prints a correctly formatted receipt on an 80mm thermal printer."""
        try:
            # Open the printer
            printer = win32print.OpenPrinter(printer_name)
            printer_dc = win32ui.CreateDC()
            printer_dc.CreatePrinterDC(printer_name)

            # Start document and page
            printer_dc.StartDoc("Queue Receipt")
            printer_dc.StartPage()

            # Set proper scaling (1 pixel = 1 unit)
            printer_dc.SetMapMode(win32con.MM_TEXT)
            current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Set large font
            font = win32ui.CreateFont({
                "name": "Arial",
                "height": 40,  # Adjust size for thermal printer readability
                "weight": win32con.FW_BOLD
            })
            printer_dc.SelectObject(font)

            # Center text horizontally
            start_x = 50  # Adjust for center alignment
            start_y = -50  # Start from top margin

            # Print each line with correct spacing

            printer_dc.TextOut(start_x + 10, start_y + LINE_HEIGHT, current_date)

            special_font = win32ui.CreateFont({
                "name": "Arial",  # Font name
                "height": 70,  # Larger font size for this specific line
                "weight": win32con.FW_BOLD  # Bold weight
            })
            printer_dc.SelectObject(special_font)

            # Print the number line with the new font size
            printer_dc.TextOut(start_x + 10, start_y + 3 * LINE_HEIGHT, f"Numri juaj : {number}")
            font = win32ui.CreateFont({
                "name": "Arial",
                "height": 30,  # Adjust size for thermal printer readability
                "weight": win32con.FW_BOLD
            })
            printer_dc.SelectObject(font)

            printer_dc.TextOut(start_x + 10, start_y + 5 * LINE_HEIGHT, "Ju lutem prisni radhen!")

            # End the document
            printer_dc.EndPage()
            printer_dc.EndDoc()
            printer_dc.DeleteDC()

            print(f"Printed receipt for number: {number}")

        except Exception as e:
            print(f"Printing error: {e}")


    print_button = CTkButton(root, text="Printo Biletën", font=("Arial", 16),
                             width=150, height=100,
                             corner_radius=32, fg_color="#164384", hover_color="#608ac6",
                             border_color="#1c5373", border_width=3, hover=True,
                             command=lambda: [increment_counter(), print_receipt(department_counters[department_name])])
    print_button.pack(pady=10)

    def go_back():
        show_departments()  # Ky funksion duhet të jetë i përshtatshëm për të kthyer në dashboard

    # Butoni për të kthyer pas (Back button)
    back_button = CTkButton(root, text="Kthehu", font=("Arial", 16), command=go_back,
                            width=150, height=100,
                            corner_radius=32, fg_color="#164384", hover_color="#608ac6",
                            border_color="#1c5373", border_width=3, hover=True,
                            )
    back_button.pack(pady=10)



def update_department_queue(dept_id, new_queue_number):
    """Update the queue number for the selected department."""
    conn = sqlite3.connect('system.db')
    c = conn.cursor()
    c.execute("UPDATE departments SET number=? WHERE id=?", (new_queue_number, dept_id))
    conn.commit()
    conn.close()


def add_department():
    """Add a new department."""
    department_name = simpledialog.askstring("Shto Departametn", "Vendosni emrin e departamentit:", parent=root)
    if department_name:
        conn = sqlite3.connect('system.db')
        c = conn.cursor()
        c.execute("INSERT INTO departments (name, number) VALUES (?, ?)", (department_name, 0))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sukses!", "Department u shtua me sukses.")
    else:
        messagebox.showwarning("Input Error", "Ju lutem vendosni nje emer te sakte te departamentit.")


def remove_department():
    """Remove an existing department."""
    department_name = simpledialog.askstring("Fshi Departament", "Vendosni nje emer departamenti:", parent=root)
    if department_name:
        conn = sqlite3.connect('system.db')
        c = conn.cursor()
        c.execute("DELETE FROM departments WHERE name=?", (department_name,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sukses!", "Departamenti u fshi me sukses!.")
    else:
        messagebox.showwarning("Input Error!", "Ju lutem vendosni nje emer te sakte te departamentit.")


def list_departments():
    """List all departments."""
    conn = sqlite3.connect('system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM departments")
    departments = c.fetchall()
    conn.close()

    if departments:
        dept_list = "\n".join([f"{dept[1]} (Number: {dept[2]})" for dept in departments])
        messagebox.showinfo("Departments", dept_list)
    else:
        messagebox.showwarning("No Departments", "No departments found.")


def update_content(clear=False):
    """Create the login screen."""
    for widget in root.winfo_children():
        widget.destroy()
    if clear:
        return

def login_screen():
    update_content(clear=True)  # Clear the current content

    label = CTkLabel(root, text="Miresevini!", width=600, height=100, font=("Manrope", 40),
                     bg_color="#4cae61",corner_radius=10, text_color="#0e3710", pady=20)
    label.pack(pady=20)

    # Login button
    login_button = CTkButton(root, text="Login", command=login, corner_radius=32, fg_color="#a97a1d", hover_color="#ddb51f",
                             border_color="#cd9628", border_width=3,
                             font=("Manrope ", 30), width=150, height=100, text_color="white", )
    login_button.pack(pady=20, )

    # Exit button
    exit_button = CTkButton(root, text="Exit", command=root.quit, font=("Arial", 30), width=150, height=100,
                            corner_radius=32, fg_color="#164384", hover_color="#608ac6",
                            border_color="#1c5373", border_width=3,hover=True,
                            )
    exit_button.pack(pady=20)


# Initialize the database and start the login screen
init_db()
frame = customtkinter.CTkFrame(master=root)
frame.pack(fill="both", expand=True)
login_screen()

root.mainloop()