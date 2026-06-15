import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "colleges.db")

# ── Palette ──────────────────────────────────────────────────────────────────
BG        = "#0F1923"   # deep navy
SURFACE   = "#162030"   # card surface
SURFACE2  = "#1E2D40"   # slightly lighter card
ACCENT    = "#00C2FF"   # electric cyan
ACCENT2   = "#FF6B35"   # warm orange (highlights / tags)
TEXT      = "#E8EDF2"
SUBTEXT   = "#7A90A4"
BORDER    = "#2A3F55"
GREEN     = "#00D68F"
ROW_ODD   = "#162030"
ROW_EVEN  = "#1A2740"

FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI", 9)
FONT_TAG     = ("Segoe UI", 10, "bold")

# ── DB helpers ────────────────────────────────────────────────────────────────
def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS colleges (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            college_id      TEXT UNIQUE NOT NULL,
            college_name    TEXT NOT NULL,
            nirf_ranking    INTEGER,
            state           TEXT,
            state_ranking   INTEGER,
            placement_pct   REAL,
            campus_acres    REAL,
            avg_package     REAL,
            highest_package REAL,
            placement_year  INTEGER,
            year_established INTEGER,
            admission_mode  TEXT
        )""")

def fetch_all(filters=None):
    q = "SELECT * FROM colleges WHERE 1=1"
    params = []
    if filters:
        if filters.get("college_name"):
            q += " AND LOWER(college_name) LIKE ?"
            params.append(f"%{filters['college_name'].lower()}%")
        if filters.get("state"):
            q += " AND LOWER(state) LIKE ?"
            params.append(f"%{filters['state'].lower()}%")
        if filters.get("admission_mode"):
            q += " AND LOWER(admission_mode) LIKE ?"
            params.append(f"%{filters['admission_mode'].lower()}%")
        if filters.get("nirf_max"):
            q += " AND nirf_ranking <= ?"
            params.append(filters["nirf_max"])
        if filters.get("placement_min"):
            q += " AND placement_pct >= ?"
            params.append(filters["placement_min"])
        if filters.get("avg_pkg_min"):
            q += " AND avg_package >= ?"
            params.append(filters["avg_pkg_min"])
    q += " ORDER BY nirf_ranking ASC NULLS LAST"
    with get_conn() as c:
        return c.execute(q, params).fetchall()

def insert_college(data):
    with get_conn() as c:
        c.execute("""
        INSERT INTO colleges
          (college_id,college_name,nirf_ranking,state,state_ranking,
           placement_pct,campus_acres,avg_package,highest_package,
           placement_year,year_established,admission_mode)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", data)

def update_college(row_id, data):
    with get_conn() as c:
        c.execute("""
        UPDATE colleges SET
          college_id=?,college_name=?,nirf_ranking=?,state=?,state_ranking=?,
          placement_pct=?,campus_acres=?,avg_package=?,highest_package=?,
          placement_year=?,year_established=?,admission_mode=?
        WHERE id=?""", (*data, row_id))

def delete_college(row_id):
    with get_conn() as c:
        c.execute("DELETE FROM colleges WHERE id=?", (row_id,))

def seed_sample_data():
    with get_conn() as c:
        if c.execute("SELECT COUNT(*) FROM colleges").fetchone()[0] > 0:
            return
    samples = [
        ("IIT001","IIT Bombay",3,"Maharashtra",1,95.2,550,24.5,1.5,2024,1958,"JEE Advanced"),
        ("IIT002","IIT Delhi",2,"Delhi",1,96.1,325,26.0,2.0,2024,1961,"JEE Advanced"),
        ("IIT003","IIT Madras",1,"Tamil Nadu",1,97.3,617,28.0,2.5,2024,1959,"JEE Advanced"),
        ("NIT001","NIT Trichy",8,"Tamil Nadu",2,88.5,800,12.5,0.85,2024,1964,"JEE Mains"),
        ("VIT001","VIT Vellore",11,"Tamil Nadu",3,82.0,392,8.5,0.65,2024,1984,"VITEEE"),
        ("IISc01","IISc Bangalore",4,"Karnataka",1,91.0,400,22.0,1.8,2024,1909,"GATE/JAM"),
        ("BITS01","BITS Pilani",25,"Rajasthan",1,85.5,328,18.5,1.2,2024,1964,"BITSAT"),
        ("IIM001","IIM Ahmedabad",1,"Gujarat",1,99.0,103,34.0,3.5,2024,1961,"CAT"),
        ("DCE001","Delhi College of Engineering",15,"Delhi",2,79.5,164,10.5,0.72,2024,1941,"JEE Mains"),
        ("PESIT1","PES University",78,"Karnataka",4,74.0,56,9.2,0.55,2024,1972,"PESSAT"),
    ]
    for s in samples:
        try:
            insert_college(s)
        except Exception:
            pass

# ── Column definitions ─────────────────────────────────────────────────────
COLS = [
    ("id","ID",40),
    ("college_id","College ID",90),
    ("college_name","College Name",220),
    ("nirf_ranking","NIRF Rank",80),
    ("state","State",130),
    ("state_ranking","State Rank",80),
    ("placement_pct","Placement %",90),
    ("campus_acres","Campus (acres)",110),
    ("avg_package","Avg Pkg (₹L)",100),
    ("highest_package","High Pkg (₹Cr)",110),
    ("placement_year","Placement Year",110),
    ("year_established","Est. Year",80),
    ("admission_mode","Admission",150),
]
COL_KEYS   = [c[0] for c in COLS]
COL_LABELS = [c[1] for c in COLS]
COL_WIDTHS = [c[2] for c in COLS]

# ── Form Dialog ────────────────────────────────────────────────────────────
class CollegeForm(tk.Toplevel):
    def __init__(self, master, title, row_data=None, on_save=None):
        super().__init__(master)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.on_save = on_save
        self.entries = {}

        fields = [
            ("college_id",      "College ID *"),
            ("college_name",    "College Name *"),
            ("nirf_ranking",    "NIRF Ranking"),
            ("state",           "State"),
            ("state_ranking",   "State Ranking"),
            ("placement_pct",   "Placement % (0–100)"),
            ("campus_acres",    "Campus Size (Acres)"),
            ("avg_package",     "Avg Package (₹ Lakhs)"),
            ("highest_package", "Highest Package (₹ Crores)"),
            ("placement_year",  "Placement Year"),
            ("year_established","Year Established"),
            ("admission_mode",  "Admission Mode"),
        ]

        tk.Label(self, text=title, font=FONT_HEADING, bg=BG, fg=ACCENT).grid(
            row=0, column=0, columnspan=2, pady=(18,12), padx=24, sticky="w")

        for i, (key, label) in enumerate(fields, start=1):
            tk.Label(self, text=label, font=FONT_BODY, bg=BG, fg=SUBTEXT, anchor="w").grid(
                row=i, column=0, padx=(24,8), pady=4, sticky="w")
            e = tk.Entry(self, font=FONT_BODY, bg=SURFACE2, fg=TEXT,
                         insertbackground=ACCENT, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=ACCENT, width=32)
            e.grid(row=i, column=1, padx=(0,24), pady=4, sticky="w")
            self.entries[key] = e

        # Pre-fill on edit
        if row_data:
            for j, key in enumerate(COL_KEYS):
                if key == "id":
                    continue
                val = row_data[j]
                if val is not None:
                    self.entries[key].insert(0, str(val))

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=16)
        tk.Button(btn_frame, text="💾  Save", font=FONT_TAG, bg=ACCENT, fg=BG,
                  relief="flat", padx=18, pady=8, cursor="hand2",
                  command=self._save).pack(side="left", padx=8)
        tk.Button(btn_frame, text="✕  Cancel", font=FONT_TAG, bg=SURFACE2, fg=SUBTEXT,
                  relief="flat", padx=18, pady=8, cursor="hand2",
                  command=self.destroy).pack(side="left", padx=8)

        self.grab_set()
        self.transient(master)

    def _save(self):
        def v(key): return self.entries[key].get().strip()
        if not v("college_id") or not v("college_name"):
            messagebox.showerror("Validation", "College ID and College Name are required.", parent=self)
            return
        def opt_int(k):
            s = v(k)
            if s == "": return None
            try: return int(s)
            except: messagebox.showerror("Validation", f"'{k}' must be an integer.", parent=self); return "ERR"
        def opt_float(k):
            s = v(k)
            if s == "": return None
            try: return float(s)
            except: messagebox.showerror("Validation", f"'{k}' must be a number.", parent=self); return "ERR"

        vals = [
            v("college_id"), v("college_name"),
            opt_int("nirf_ranking"), v("state"), opt_int("state_ranking"),
            opt_float("placement_pct"), opt_float("campus_acres"),
            opt_float("avg_package"), opt_float("highest_package"),
            opt_int("placement_year"), opt_int("year_established"),
            v("admission_mode") or None,
        ]
        if "ERR" in [str(x) for x in vals]:
            return
        if self.on_save:
            self.on_save(vals)
        self.destroy()

# ── Main App ───────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("College Data Manager")
        self.configure(bg=BG)
        self.geometry("1280x780")
        self.minsize(1000, 600)
        init_db()
        seed_sample_data()
        self._build_ui()
        self._load_table()

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=SURFACE, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="🎓", font=("Segoe UI Emoji", 20), bg=SURFACE, fg=ACCENT).pack(side="left", padx=(20,6))
        tk.Label(header, text="College Data Manager", font=FONT_TITLE, bg=SURFACE, fg=TEXT).pack(side="left")
        tk.Label(header, text="India's College Intelligence Platform",
                 font=FONT_SMALL, bg=SURFACE, fg=SUBTEXT).pack(side="left", padx=12, pady=(8,0))

        # ── Stats bar ───────────────────────────────────────────────────────
        self.stat_frame = tk.Frame(self, bg=BG, pady=6)
        self.stat_frame.pack(fill="x", padx=18, pady=(10,0))

        # ── Filter panel ────────────────────────────────────────────────────
        filter_outer = tk.Frame(self, bg=SURFACE, pady=12)
        filter_outer.pack(fill="x", padx=18, pady=8)
        tk.Label(filter_outer, text="  🔍  Filters", font=FONT_TAG, bg=SURFACE, fg=ACCENT).pack(side="left")

        self.f_name  = self._filter_entry(filter_outer, "College Name")
        self.f_state = self._filter_entry(filter_outer, "State")
        self.f_adm   = self._filter_entry(filter_outer, "Admission Mode")
        self.f_nirf  = self._filter_entry(filter_outer, "NIRF ≤", width=7)
        self.f_plc   = self._filter_entry(filter_outer, "Placement % ≥", width=7)
        self.f_pkg   = self._filter_entry(filter_outer, "Avg Pkg ≥ (₹L)", width=8)

        tk.Button(filter_outer, text="Apply", font=FONT_TAG, bg=ACCENT, fg=BG,
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=self._apply_filters).pack(side="left", padx=(12,4))
        tk.Button(filter_outer, text="Clear", font=FONT_TAG, bg=SURFACE2, fg=SUBTEXT,
                  relief="flat", padx=12, pady=4, cursor="hand2",
                  command=self._clear_filters).pack(side="left", padx=4)

        # ── Action buttons ───────────────────────────────────────────────────
        act = tk.Frame(self, bg=BG)
        act.pack(fill="x", padx=18, pady=(0,6))
        for label, color, cmd in [
            ("＋  Add College", GREEN, self._add),
            ("✎  Edit", ACCENT, self._edit),
            ("🗑  Delete", ACCENT2, self._delete),
        ]:
            tk.Button(act, text=label, font=FONT_TAG, bg=color, fg=BG,
                      relief="flat", padx=14, pady=6, cursor="hand2",
                      command=cmd).pack(side="left", padx=(0,8))

        # ── Table ────────────────────────────────────────────────────────────
        table_frame = tk.Frame(self, bg=BG)
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0,14))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("College.Treeview",
            background=ROW_ODD, foreground=TEXT,
            fieldbackground=ROW_ODD, rowheight=28,
            borderwidth=0, relief="flat", font=FONT_BODY)
        style.configure("College.Treeview.Heading",
            background=SURFACE2, foreground=ACCENT,
            font=FONT_TAG, borderwidth=0, relief="flat")
        style.map("College.Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", BG)])

        self.tree = ttk.Treeview(table_frame, style="College.Treeview",
                                  columns=COL_KEYS, show="headings",
                                  selectmode="browse")

        for key, label, width in COLS:
            self.tree.heading(key, text=label,
                              command=lambda k=key: self._sort(k))
            anchor = "center" if key not in ("college_name","state","admission_mode") else "w"
            self.tree.column(key, width=width, anchor=anchor, minwidth=40)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("odd",  background=ROW_ODD)
        self.tree.tag_configure("even", background=ROW_EVEN)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var, font=FONT_SMALL,
                 bg=SURFACE, fg=SUBTEXT, anchor="w", pady=5).pack(fill="x", side="bottom")

        self._sort_col = None
        self._sort_rev = False

    def _filter_entry(self, parent, placeholder, width=14):
        frame = tk.Frame(parent, bg=SURFACE)
        frame.pack(side="left", padx=(10,0))
        tk.Label(frame, text=placeholder, font=FONT_SMALL, bg=SURFACE, fg=SUBTEXT).pack()
        e = tk.Entry(frame, font=FONT_BODY, bg=SURFACE2, fg=TEXT,
                     insertbackground=ACCENT, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=ACCENT, width=width)
        e.pack()
        return e

    def _load_table(self, filters=None):
        rows = fetch_all(filters)
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            display = list(row)
            # Format numeric cols
            if display[6] is not None:  display[6] = f"{display[6]:.1f}%"
            if display[7] is not None:  display[7] = f"{display[7]:,.0f}"
            if display[8] is not None:  display[8] = f"₹{display[8]:.1f}L"
            if display[9] is not None:  display[9] = f"₹{display[9]:.2f}Cr"
            self.tree.insert("", "end", iid=str(row[0]),
                             values=display, tags=(tag,))
        self._update_stats(rows)
        self.status_var.set(f"{len(rows)} college(s) found")

    def _update_stats(self, rows):
        for w in self.stat_frame.winfo_children():
            w.destroy()
        total = len(rows)
        states = len(set(r[4] for r in rows if r[4]))
        avg_nirf = sum(r[3] for r in rows if r[3]) / max(1, sum(1 for r in rows if r[3]))
        avg_pkg  = sum(r[8] for r in rows if r[8]) / max(1, sum(1 for r in rows if r[8]))
        for label, val in [
            ("Total Colleges", str(total)),
            ("States Covered", str(states)),
            ("Avg NIRF Rank", f"{avg_nirf:.0f}"),
            ("Avg Package", f"₹{avg_pkg:.1f}L"),
        ]:
            card = tk.Frame(self.stat_frame, bg=SURFACE2, padx=18, pady=8)
            card.pack(side="left", padx=(0,10))
            tk.Label(card, text=val, font=("Segoe UI", 16, "bold"),
                     bg=SURFACE2, fg=ACCENT).pack()
            tk.Label(card, text=label, font=FONT_SMALL, bg=SURFACE2, fg=SUBTEXT).pack()

    def _apply_filters(self):
        def g(e): return e.get().strip() or None
        def gf(e):
            s = e.get().strip()
            try: return float(s) if s else None
            except: return None
        self._load_table({
            "college_name":  g(self.f_name),
            "state":         g(self.f_state),
            "admission_mode":g(self.f_adm),
            "nirf_max":      gf(self.f_nirf),
            "placement_min": gf(self.f_plc),
            "avg_pkg_min":   gf(self.f_pkg),
        })

    def _clear_filters(self):
        for e in [self.f_name, self.f_state, self.f_adm, self.f_nirf, self.f_plc, self.f_pkg]:
            e.delete(0, "end")
        self._load_table()

    def _get_selected_row(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Please select a college first.")
            return None, None
        row_id = int(sel[0])
        vals = self.tree.item(sel[0], "values")
        return row_id, vals

    def _add(self):
        def save(data):
            try:
                insert_college(data)
                self._apply_filters()
                messagebox.showinfo("Success", "College added successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "College ID already exists.")
        CollegeForm(self, "Add New College", on_save=save)

    def _edit(self):
        row_id, vals = self._get_selected_row()
        if row_id is None:
            return
        # Fetch raw from DB for editing
        with get_conn() as c:
            raw = c.execute("SELECT * FROM colleges WHERE id=?", (row_id,)).fetchone()
        def save(data):
            update_college(row_id, data)
            self._apply_filters()
            messagebox.showinfo("Success", "College updated successfully!")
        CollegeForm(self, "Edit College", row_data=raw, on_save=save)

    def _delete(self):
        row_id, vals = self._get_selected_row()
        if row_id is None:
            return
        name = vals[2]
        if messagebox.askyesno("Confirm Delete", f"Delete '{name}'?\nThis cannot be undone."):
            delete_college(row_id)
            self._apply_filters()
            self.status_var.set(f"Deleted: {name}")

    def _sort(self, col):
        rows = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        reverse = (self._sort_col == col) and not self._sort_rev
        try:
            rows.sort(key=lambda x: float(x[0].replace("₹","").replace("L","").replace("Cr","").replace("%","").replace(",","")) if x[0] else float("inf"), reverse=reverse)
        except ValueError:
            rows.sort(key=lambda x: x[0].lower(), reverse=reverse)
        for i, (_, k) in enumerate(rows):
            self.tree.move(k, "", i)
            self.tree.item(k, tags=("even" if i%2==0 else "odd",))
        self._sort_col = col
        self._sort_rev = reverse

if __name__ == "__main__":
    app = App()
    app.mainloop()
