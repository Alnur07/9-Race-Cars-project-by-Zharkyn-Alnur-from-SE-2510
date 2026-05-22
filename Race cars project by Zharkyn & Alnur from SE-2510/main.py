# main.py
import sys
import os
import json
import tkinter as tk
from tkinter import messagebox, ttk

# Fix import paths for stable project structure
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from Cars.vehicle import RaceCar, StreetCar
from Manager.manage import GarageManager, AVAILABLE_TRACKS
from utils import validate_record_time, time_to_ms


def normalize_time_format(time_str: str) -> str:
    """Normalize time to unified MM:SS:ms standard (e.g., 1:42:35 -> 01:42:35)."""
    try:
        parts = [p.strip() for p in time_str.split(':')]
        if len(parts) == 3:
            return f"{int(parts[0]):02d}:{int(parts[1]):02d}:{int(parts[2]):02d}"
    except Exception:
        pass
    return time_str


class RaceCarApp:
    """Main GUI application for race car track leaderboard management."""

    def __init__(self, root):
        """Initialize the GUI application with all widgets and data bindings.

        Args:
            root: tk.Tk root window instance
        """
        self.manager = GarageManager()
        self.root = root
        self.root.title("Race Car Management System")
        self.root.geometry("1050x680")
        self.root.configure(bg="#f0f2f5")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        title_label = tk.Label(
            root,
            text="🏎️ Race Car Track Leaderboard",
            font=("Helvetica", 18, "bold"),
            bg="#f0f2f5",
            fg="#1a202c"
        )
        title_label.pack(pady=15)

        main_frame = tk.Frame(root, bg="#f0f2f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Left panel - Actions
        left_panel = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)

        tk.Label(
            left_panel,
            text="Actions",
            font=("Helvetica", 12, "bold"),
            bg="#ffffff",
            fg="#4a5568"
        ).pack(pady=10, padx=20)

        ttk.Button(left_panel, text="🔄 Load Global Database",
                   command=self.load_global_session).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(left_panel, text="➕ Register New Vehicle",
                   command=self.add_car_window).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(left_panel, text="⏱️ Add/Edit Record Time",
                   command=self.add_record_window).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(left_panel, text="💾 Save Database to JSON",
                   command=self.save_global_session).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(left_panel, text="📊 Advanced Statistics",
                   command=self.open_stats_window).pack(fill=tk.X, padx=15, pady=5)

        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=15, padx=15)
        ttk.Button(left_panel, text="❌ Exit System", command=root.quit).pack(fill=tk.X, padx=15, pady=5)

        # Right panel - Tabs
        right_panel = tk.Frame(main_frame, bg="#f0f2f5")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: All Cars
        self.tab_all_cars = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_all_cars, text="🚗 Active Roster (All Cars)")

        columns = ("#1", "#2", "#3", "#4", "#5", "#6")
        self.tree_all = ttk.Treeview(self.tab_all_cars, columns=columns, show="headings")
        self.tree_all.heading("#1", text="ID")
        self.tree_all.heading("#2", text="Brand")
        self.tree_all.heading("#3", text="Model")
        self.tree_all.heading("#4", text="Mileage")
        self.tree_all.heading("#5", text="Type")
        self.tree_all.heading("#6", text="Specs (Seats/Tracks)")

        self.tree_all.column("#1", width=50, anchor=tk.CENTER)
        self.tree_all.column("#2", width=120)
        self.tree_all.column("#3", width=120)
        self.tree_all.column("#4", width=110, anchor=tk.CENTER)
        self.tree_all.column("#5", width=110, anchor=tk.CENTER)
        self.tree_all.column("#6", width=160)
        self.tree_all.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 2: Leaderboard
        self.tab_records = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_records, text="🏆 Sorted Leaderboard")

        track_filter_frame = tk.Frame(self.tab_records, bg="#f0f2f5")
        track_filter_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(track_filter_frame, text="Select Track to View: ",
                 font=("Helvetica", 10, "bold"), bg="#f0f2f5").pack(side=tk.LEFT, padx=5)

        self.track_view_combo = ttk.Combobox(
            track_filter_frame,
            values=list(AVAILABLE_TRACKS),
            state="readonly",
            width=15
        )
        self.track_view_combo.set(AVAILABLE_TRACKS[0])
        self.track_view_combo.pack(side=tk.LEFT, padx=5)
        self.track_view_combo.bind("<<ComboboxSelected>>", lambda e: self.update_tables())

        columns_rec = ("#1", "#2", "#3", "#4", "#5")
        self.tree_records = ttk.Treeview(self.tab_records, columns=columns_rec, show="headings")
        self.tree_records.heading("#1", text="Rank")
        self.tree_records.heading("#2", text="Brand")
        self.tree_records.heading("#3", text="Model")
        self.tree_records.heading("#4", text="Best Time")
        self.tree_records.heading("#5", text="Year")

        self.tree_records.column("#1", width=60, anchor=tk.CENTER)
        self.tree_records.column("#2", width=120)
        self.tree_records.column("#3", width=120)
        self.tree_records.column("#4", width=140, anchor=tk.CENTER)
        self.tree_records.column("#5", width=100, anchor=tk.CENTER)
        self.tree_records.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Auto-load database on startup
        if self.manager.load_from_json():
            print("Global database auto-loaded.")
        self.update_tables()

    def update_tables(self):
        """Refresh both Treeview tables with current manager data."""
        for item in self.tree_all.get_children():
            self.tree_all.delete(item)
        for item in self.tree_records.get_children():
            self.tree_records.delete(item)

        # Update Active Roster table
        for idx, car in enumerate(self.manager.cars, start=1):
            car_type = type(car).__name__
            specs_info = ""
            if isinstance(car, StreetCar):
                specs_info = f"🛋️ Seats: {car.passenger_seats}"
            elif isinstance(car, RaceCar):
                specs_info = f"🏁 Tracks Logged: {len(car.records)}"

            self.tree_all.insert("", tk.END, values=(
                idx, car.brand, car.model, f"{car.mileage} km", car_type, specs_info
            ))

        # Update Leaderboard
        selected_track = self.track_view_combo.get()
        leaderboard_data = []

        for car in self.manager.cars:
            if isinstance(car, RaceCar) and selected_track in car.records and car.records[selected_track]:
                best_year = min(
                    car.records[selected_track],
                    key=lambda y: time_to_ms(car.records[selected_track][y])
                )
                best_time = car.records[selected_track][best_year]
                display_time = normalize_time_format(best_time)

                leaderboard_data.append({
                    "car": car,
                    "time": display_time,
                    "ms": time_to_ms(best_time),
                    "year": best_year
                })

        leaderboard_data.sort(key=lambda x: x["ms"])

        for rank, data in enumerate(leaderboard_data, start=1):
            car = data["car"]
            self.tree_records.insert("", tk.END, values=(
                rank, car.brand, car.model, data["time"], data["year"]
            ))

    def load_global_session(self):
        """Load database from JSON and refresh tables."""
        if self.manager.load_from_json():
            self.update_tables()
            messagebox.showinfo("Success", "Global database loaded successfully!")
        else:
            messagebox.showwarning("Not Found", "Database file 'garage_database.json' not found or empty.")

    def save_global_session(self):
        """Save current state to JSON database."""
        self.manager.save_to_json()
        messagebox.showinfo("Saved", "Database saved successfully!")

    def add_car_window(self):
        """Open dialog window for registering new vehicles."""
        win = tk.Toplevel(self.root)
        win.title("Register New Vehicle")
        win.geometry("360x420")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Select Vehicle Category:", font=("Helvetica", 10, "bold")).pack(pady=10)

        type_var = tk.StringVar(value="RaceCar")
        type_combo = ttk.Combobox(win, textvariable=type_var, values=["RaceCar", "StreetCar"], state="readonly")
        type_combo.pack(pady=2)

        fields_frame = tk.Frame(win, pady=10)
        fields_frame.pack(fill=tk.X, padx=25)

        tk.Label(fields_frame, text="Brand:").pack(anchor=tk.W)
        entry_brand = ttk.Entry(fields_frame)
        entry_brand.pack(fill=tk.X, pady=2)

        tk.Label(fields_frame, text="Model:").pack(anchor=tk.W)
        entry_model = ttk.Entry(fields_frame)
        entry_model.pack(fill=tk.X, pady=2)

        tk.Label(fields_frame, text="Mileage (km):").pack(anchor=tk.W)
        entry_mileage = ttk.Entry(fields_frame)
        entry_mileage.pack(fill=tk.X, pady=2)

        lbl_seats = tk.Label(fields_frame, text="Passenger Seats Count:",
                             fg="#c2410c", font=("Helvetica", 9, "bold"))
        entry_seats = ttk.Entry(fields_frame)
        entry_seats.insert(0, "5")

        def toggle_fields(event=None):
            """Show/hide seats field based on vehicle type selection."""
            if type_var.get() == "StreetCar":
                lbl_seats.pack(anchor=tk.W, pady=(5, 0))
                entry_seats.pack(fill=tk.X, pady=2)
            else:
                lbl_seats.pack_forget()
                entry_seats.pack_forget()

        type_combo.bind("<<ComboboxSelected>>", toggle_fields)

        def submit_car():
            """Validate inputs and add new car to manager."""
            brand, model = entry_brand.get().strip(), entry_model.get().strip()
            try:
                mileage = int(entry_mileage.get().strip())
                if not brand or not model:
                    raise ValueError
                if mileage < 0:
                    raise ValueError

                if type_var.get() == "StreetCar":
                    seats = int(entry_seats.get().strip())
                    new_car = StreetCar(brand, model, mileage, p_seats=seats)
                else:
                    new_car = RaceCar(brand, model, mileage)

                self.manager.add_car(new_car)
                self.update_tables()
                messagebox.showinfo("Success", f"{type_var.get()} '{brand} {model}' registered!", parent=win)
                win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid inputs. Check numeric values and ensure mileage >= 0.", parent=win)

        ttk.Button(win, text="Confirm Registration", command=submit_car).pack(pady=20)

    def add_record_window(self):
        """Open dialog for adding track records to selected RaceCar."""
        current_tab = self.notebook.index(self.notebook.select())
        tree_source = self.tree_all if current_tab == 0 else self.tree_records

        selected = tree_source.selection()
        if not selected:
            messagebox.showwarning("Selection", "Select a car from the active table first!")
            return

        item_values = tree_source.item(selected[0], 'values')
        brand_name, model_name = item_values[1], item_values[2]

        target_car = next((c for c in self.manager.cars
                          if c.brand == brand_name and c.model == model_name), None)
        if not target_car:
            return

        # Polymorphism check: StreetCar cannot have track records
        if isinstance(target_car, StreetCar):
            messagebox.showerror("Polymorphism Error",
                f"'{brand_name} {model_name}' is a StreetCar!\n"
                "Track records can only be appended to RaceCar objects.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"New Record for {target_car.model}")
        win.geometry("350x260")
        win.grab_set()

        tk.Label(win, text="Select Track:").pack(pady=2)
        combo_track = ttk.Combobox(win, values=list(AVAILABLE_TRACKS), state="readonly")
        combo_track.set(AVAILABLE_TRACKS[0])
        combo_track.pack(pady=2)

        tk.Label(win, text="Enter Year:").pack(pady=2)
        entry_year = ttk.Entry(win)
        entry_year.pack(pady=2)
        entry_year.insert(0, "2026")

        tk.Label(win, text="Enter Time (MM:SS:ms):").pack(pady=2)
        entry_time = ttk.Entry(win)
        entry_time.pack(pady=2)
        entry_time.insert(0, "01:45:20")

        def submit_record():
            """Validate and save track record."""
            try:
                track = combo_track.get()
                year = int(entry_year.get())
                time_val = entry_time.get().strip()
                if validate_record_time(time_val):
                    formatted_time = normalize_time_format(time_val)
                    target_car.add_record(track, year, formatted_time)
                    self.update_tables()
                    messagebox.showinfo("Success", f"Record added for {track}!", parent=win)
                    win.destroy()
                else:
                    messagebox.showerror("Format Error", "Use strict MM:SS:ms (e.g., 01:52:02).", parent=win)
            except ValueError:
                messagebox.showerror("Error", "Check your inputs.", parent=win)

        ttk.Button(win, text="Save Record", command=submit_record).pack(pady=15)

    def open_stats_window(self):
        """Open advanced statistics panel with generator, lambda, and map demos."""
        win = tk.Toplevel(self.root)
        win.title("Advanced Analytical Panel")
        win.geometry("550x450")

        notebook = ttk.Notebook(win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Brand Filter (Generator)
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Brand Filter (Generator)")
        tk.Label(tab1, text="Enter Brand Name:", font=("Helvetica", 10, "bold")).pack(pady=5)
        entry_b = ttk.Entry(tab1, width=25)
        entry_b.pack(pady=2)
        txt_b = tk.Text(tab1, height=12, width=60, font=("Courier New", 10))

        def run_brand_filter():
            """Execute generator stream for brand filtering."""
            txt_b.delete("1.0", tk.END)
            search_brand = entry_b.get().strip()
            if not search_brand:
                return
            gen = self.manager.generate_cars_by_brand(search_brand)
            txt_b.insert(tk.END, f"--- Streaming results for '{search_brand}' ---\n")
            for car in gen:
                car_type = type(car).__name__
                txt_b.insert(tk.END, f"• {car.brand} {car.model} | {car.mileage} km | [{car_type}]\n")
                if isinstance(car, RaceCar) and car.records:
                    for track, years in car.records.items():
                        formatted_years = {y: normalize_time_format(t) for y, t in years.items()}
                        txt_b.insert(tk.END, f"   ↳ {track}: {formatted_years}\n")

        ttk.Button(tab1, text="Run Generator Stream", command=run_brand_filter).pack(pady=5)
        txt_b.pack(pady=5, padx=10)

        # Tab 2: Mileage Filter (Lambda)
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Mileage Filter (Lambda)")
        tk.Label(tab2, text="Enter Mileage Threshold (km):", font=("Helvetica", 10, "bold")).pack(pady=5)
        entry_m = ttk.Entry(tab2, width=25)
        entry_m.pack(pady=2)
        var_op = tk.StringVar(value=">")
        radio_frame = tk.Frame(tab2)
        radio_frame.pack(pady=2)
        tk.Radiobutton(radio_frame, text=">", variable=var_op, value=">").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(radio_frame, text="<", variable=var_op, value="<").pack(side=tk.LEFT, padx=10)
        txt_m = tk.Text(tab2, height=10, width=60, font=("Courier New", 10))

        def run_mileage_filter():
            """Apply lambda filter for mileage threshold."""
            txt_m.delete("1.0", tk.END)
            try:
                limit = int(entry_m.get().strip())
                operator = var_op.get()
                res = self.manager.get_filtered_mileage_cars(limit, operator=operator)
                for car in res:
                    txt_m.insert(tk.END, f"• {car.brand} {car.model} ({car.mileage} km) [{type(car).__name__}]\n")
            except ValueError:
                pass

        ttk.Button(tab2, text="Apply Lambda Filter", command=run_mileage_filter).pack(pady=5)
        txt_m.pack(pady=5, padx=10)

        # Tab 3: Map
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Models Upper (Map)")
        txt_map = tk.Text(tab3, height=12, width=60, font=("Courier New", 10))

        def run_map_upper():
            """Execute map formatting for uppercase model names."""
            txt_map.delete("1.0", tk.END)
            models = self.manager.get_all_car_models_uppercase()
            txt_map.insert(tk.END, "Result list:\n" + str(models))

        ttk.Button(tab3, text="Execute Map Formatting", command=run_map_upper).pack(pady=5)
        txt_map.pack(pady=5, padx=10)


def main():
    """Entry point: display menu and launch GUI or CSV export on user selection."""
    manager = GarageManager()  # Create manager instance for CLI operations
    running = True

    while running:
        print("\n=== MAIN MENU ===")
        print("1. Launch Application")
        print("2. Export Track Records to CSV")
        print("3. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            root = tk.Tk()
            app = RaceCarApp(root)
            root.mainloop()

        elif choice == "2":
            # Auto-load database before export
            if not manager.cars:
                manager.load_from_json()
                if not manager.cars:
                    print("✗ No cars in database. Add cars in GUI first (option 1).")
                    continue

            print("\nAvailable tracks:", ", ".join(AVAILABLE_TRACKS))
            track = input("Enter track name: ").strip()
            if track in AVAILABLE_TRACKS:
                try:
                    path = manager.export_records_to_csv(track)
                    # Check if file has content
                    with open(path, 'r') as f:
                        lines = f.readlines()
                    if len(lines) <= 1:
                        print(f"⚠ CSV created but empty — no records for {track}")
                        print("  Add track records in GUI first.")
                    else:
                        print(f"✓ Exported {len(lines)-1} records to: {path}")
                except Exception as e:
                    print(f"✗ Export failed: {e}")
            else:
                print("✗ Invalid track name")

        elif choice == "3":
            print("Exiting...")
            running = False
            sys.exit(0)

        else:
            print("Invalid option")


if __name__ == "__main__":
    main()