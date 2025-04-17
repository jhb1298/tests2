import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


# Create the database and payroll table if they don't exist
def create_payroll_db():
    conn = sqlite3.connect('payroll.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS payroll (
                        employee_id TEXT PRIMARY KEY,
                        employee_name TEXT NOT NULL,
                        position TEXT NOT NULL,
                        monthly_salary REAL NOT NULL,
                        bonus REAL DEFAULT 0.0
                    )''')
    conn.commit()
    conn.close()


class PayrollApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Payroll Management System")
        self.root.geometry("800x650")  # Set default window size
        self.root.resizable(True, True)  # Allow resizing

        # Outer frame with padding
        self.outer_frame = tk.Frame(self.root, padx=80, pady=12)  # 10% left/right, 5% top/bottom
        self.outer_frame.pack(fill="both", expand=True)

        # App Heading
        self.heading_label = tk.Label(self.outer_frame, text="Employee Payroll Management System",
                              font=("Arial", 20, "bold"), fg="#333333")
        self.heading_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Variables for input fields
        self.employee_name_var = tk.StringVar()
        self.employee_id_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.monthly_salary_var = tk.StringVar()
        self.bonus_var = tk.StringVar()
        self.search_var = tk.StringVar()

        # Input fields with placeholders
        self.create_placeholder_entry(
            self.outer_frame, "Employee Name:", self.employee_name_var, "Enter full name", 1,
            "Enter the name of the employee."
        )
        self.create_placeholder_entry(
            self.outer_frame, "Employee ID:", self.employee_id_var, "Enter unique ID", 2,
            "Enter a unique identification number for the employee."
        )
        self.create_placeholder_entry(
            self.outer_frame, "Position:", self.position_var, "Enter position", 3,
            "Enter the job position of the employee."
        )
        self.create_placeholder_entry(
            self.outer_frame, "Monthly Salary:", self.monthly_salary_var, "Enter salary (e.g., 5000)", 4,
            "Enter the monthly salary of the employee."
        )
        self.create_placeholder_entry(
            self.outer_frame, "Bonus:", self.bonus_var, "Enter bonus (optional)", 5,
            "Enter any bonus the employee is eligible for (optional)."
        )

        # Buttons
        tk.Button(self.outer_frame, text="Add Employee", command=self.add_employee).grid(row=7, column=0, padx=10, pady=10, sticky="ew")
        tk.Button(self.outer_frame, text="Clear Fields", command=self.clear_fields).grid(row=7, column=1, padx=10, pady=10, sticky="ew")
        tk.Button(self.outer_frame, text="Show Payroll", command=self.show_payroll).grid(row=8, column=0, padx=10, pady=10, sticky="ew")
        tk.Button(self.outer_frame, text="Update Salary", command=self.update_salary).grid(row=8, column=1, padx=10, pady=10, sticky="ew")

        # Search Field and Button
        search_frame = tk.Frame(self.outer_frame)
        search_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        tk.Label(search_frame, text="Search by ID or Position:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(search_frame, textvariable=self.search_var).grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        tk.Button(search_frame, text="Search", command=self.search_employee).grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        # Payroll Treeview
        columns = ("employee_id", "employee_name", "position", "monthly_salary", "bonus")
        self.tree = ttk.Treeview(self.outer_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
        self.tree.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configure resizing behavior
        self.outer_frame.grid_columnconfigure(0, weight=1, uniform="equal")
        self.outer_frame.grid_columnconfigure(1, weight=1, uniform="equal")
        self.outer_frame.grid_rowconfigure(10, weight=1)
        search_frame.grid_columnconfigure(1, weight=3)
        search_frame.grid_columnconfigure(2, weight=1)

    def create_placeholder_entry(self, root, label_text, variable, placeholder, row, tooltip_text):
        tk.Label(root, text=label_text).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(root, textvariable=variable, fg="gray")
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        entry.insert(0, placeholder)

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg="black")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="gray")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        # Tooltip display
        entry.bind("<Enter>", lambda event, tooltip=tooltip_text: self.show_tooltip(event, tooltip))
        entry.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event, tooltip_text):
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root+15}")
        label = tk.Label(self.tooltip, text=tooltip_text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def add_employee(self):
        employee_id = self.employee_id_var.get().strip()
        employee_name = self.employee_name_var.get().strip()
        position = self.position_var.get().strip()
        monthly_salary = self.monthly_salary_var.get().strip()
        bonus = self.bonus_var.get().strip()

        if not (employee_id and employee_name and position and monthly_salary):
            messagebox.showerror("Input Error", "All fields except Bonus are mandatory!")
            return

        try:
            monthly_salary = float(monthly_salary)
            bonus = float(bonus) if bonus else 0.0
        except ValueError:
            messagebox.showerror("Input Error", "Salary and Bonus must be numeric values!")
            return

        try:
            conn = sqlite3.connect('payroll.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO payroll VALUES (?, ?, ?, ?, ?)', (employee_id, employee_name, position, monthly_salary, bonus))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Employee added successfully!")
            self.clear_fields()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Employee ID already exists!")

    def clear_fields(self):
        self.employee_id_var.set("")
        self.employee_name_var.set("")
        self.position_var.set("")
        self.monthly_salary_var.set("")
        self.bonus_var.set("")

    def show_payroll(self):
        conn = sqlite3.connect('payroll.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payroll')
        rows = cursor.fetchall()
        conn.close()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def search_employee(self):
        search_term = self.search_var.get().strip()
        conn = sqlite3.connect('payroll.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payroll WHERE employee_id LIKE ? OR position LIKE ?", (f"%{search_term}%", f"%{search_term}%"))
        rows = cursor.fetchall()
        conn.close()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def update_salary(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an employee to update.")
            return

        item = self.tree.item(selected_item)
        employee_id = item['values'][0]
        new_salary = messagebox.askstring("Update Salary", "Enter new monthly salary:")

        if not new_salary:
            return

        try:
            new_salary = float(new_salary)
        except ValueError:
            messagebox.showerror("Input Error", "Salary must be a numeric value!")
            return

        conn = sqlite3.connect('payroll.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE payroll SET monthly_salary = ? WHERE employee_id = ?', (new_salary, employee_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Salary updated successfully!")
        self.show_payroll()


def main():
    create_payroll_db()
    root = tk.Tk()
    app = PayrollApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
