"""
โปรแกรมรวมคะแนนและตัดเกรด
วิชา Basic Computer Programming
จำนวนนักศึกษา 20 คน (Midterm + Final)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

NUM_STUDENTS = 20
FONT_NAME = "Tahoma"          # ฟอนต์ที่มีในเครื่องแทบทุกเครื่อง รองรับภาษาไทยดี

# ---------------- โทนสี ----------------
BG          = "#eef1f6"
PRIMARY     = "#4f46e5"
PRIMARY_DK  = "#3730a3"
CARD_BG     = "#ffffff"
BORDER      = "#e2e5ec"
TEXT_DARK   = "#1f2430"
TEXT_MUTED  = "#6b7280"
ROW_ALT     = "#f7f8fc"
DANGER      = "#ef4444"
SUCCESS     = "#22c55e"
INFO        = "#0ea5e9"
PURPLE      = "#8b5cf6"

# ---------------- เกณฑ์การตัดเกรด (แก้ไขได้ตามต้องการ) ----------------
GRADE_SCALE = [
    (80, 100, "A"),
    (75, 79.99, "B+"),
    (70, 74.99, "B"),
    (65, 69.99, "C+"),
    (60, 64.99, "C"),
    (55, 59.99, "D+"),
    (50, 54.99, "D"),
    (0,  49.99, "F"),
]

GRADE_POINT = {"A": 4.0, "B+": 3.5, "B": 3.0, "C+": 2.5,
               "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0}

GRADE_COLOR = {
    "A": "#16a34a", "B+": "#65a30d", "B": "#ca8a04",
    "C+": "#d97706", "C": "#ea580c", "D+": "#dc2626",
    "D": "#dc2626", "F": "#991b1b",
}


def get_grade(percent):
    for low, high, grade in GRADE_SCALE:
        if low <= percent <= high:
            return grade
    return "F"


class GradeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("รวมคะแนน & ตัดเกรด • Basic Computer Programming")
        self.geometry("1040x760")
        self.minsize(900, 640)
        self.configure(bg=BG)

        self.rows = []
        self._init_style()
        self._build_header()
        self._build_config_bar()
        self._build_stat_cards()
        self._build_table()
        self._build_bottom_bar()

    # ---------------- ttk style ----------------
    def _init_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD_BG)

        style.configure("Scroll.Vertical.TScrollbar",
                         background=BORDER, troughcolor=BG, bordercolor=BG,
                         arrowcolor=TEXT_MUTED, relief="flat")

        def make_btn_style(name, color, hover):
            style.configure(f"{name}.TButton",
                             background=color, foreground="white",
                             font=(FONT_NAME, 12, "bold"),
                             padding=(14, 10), borderwidth=0, relief="flat")
            style.map(f"{name}.TButton",
                      background=[("active", hover), ("pressed", hover)])

        make_btn_style("Primary", PRIMARY, PRIMARY_DK)
        make_btn_style("Info", INFO, "#0284c7")
        make_btn_style("Purple", PURPLE, "#7c3aed")
        make_btn_style("Danger", DANGER, "#dc2626")

    # ---------------- Header ----------------
    def _build_header(self):
        header = tk.Frame(self, bg=PRIMARY, height=92)
        header.pack(fill="x")
        header.pack_propagate(False)

        wrap = tk.Frame(header, bg=PRIMARY)
        wrap.pack(expand=True, fill="both", padx=28)

        tk.Label(wrap, text="📊  รวมคะแนนและตัดเกรด", bg=PRIMARY, fg="white",
                 font=(FONT_NAME, 20, "bold")).pack(anchor="w", pady=(14, 0))
        tk.Label(wrap, text="Basic Computer Programming  •  นักศึกษา 20 คน  •  Midterm + Final",
                 bg=PRIMARY, fg="#e0e7ff",
                 font=(FONT_NAME, 11)).pack(anchor="w")

    # ---------------- แถบตั้งค่าคะแนนเต็ม ----------------
    def _build_config_bar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=28, pady=(16, 8))

        card = tk.Frame(bar, bg=CARD_BG, highlightbackground=BORDER,
                         highlightthickness=1)
        card.pack(fill="x")
        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(fill="x", padx=18, pady=12)

        tk.Label(inner, text="คะแนนเต็ม", bg=CARD_BG, fg=TEXT_DARK,
                 font=(FONT_NAME, 12, "bold")).pack(side="left", padx=(0, 16))

        tk.Label(inner, text="Midterm", bg=CARD_BG, fg=TEXT_MUTED,
                 font=(FONT_NAME, 11)).pack(side="left")
        self.max_mid_var = tk.StringVar(value="50")
        tk.Entry(inner, textvariable=self.max_mid_var, width=5, justify="center",
                 font=(FONT_NAME, 11), relief="solid", bd=1,
                 highlightthickness=0).pack(side="left", padx=(6, 18))

        tk.Label(inner, text="Final", bg=CARD_BG, fg=TEXT_MUTED,
                 font=(FONT_NAME, 11)).pack(side="left")
        self.max_final_var = tk.StringVar(value="50")
        tk.Entry(inner, textvariable=self.max_final_var, width=5, justify="center",
                 font=(FONT_NAME, 11), relief="solid", bd=1,
                 highlightthickness=0).pack(side="left", padx=(6, 18))

        tk.Label(inner, text="* คะแนนรวมจะแปลงเป็น % ของคะแนนเต็มก่อนตัดเกรด",
                 bg=CARD_BG, fg=TEXT_MUTED, font=(FONT_NAME, 10)).pack(side="left")

    # ---------------- การ์ดสรุปสถิติ ----------------
    def _build_stat_cards(self):
        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="x", padx=28, pady=(0, 12))

        self.stat_vars = {
            "count": tk.StringVar(value="0 / 20"),
            "avg": tk.StringVar(value="-"),
            "gpa": tk.StringVar(value="-"),
            "top": tk.StringVar(value="-"),
        }
        specs = [
            ("count", "จำนวนที่กรอกแล้ว", INFO),
            ("avg",   "คะแนนเฉลี่ย", PRIMARY),
            ("gpa",   "GPA เฉลี่ย", PURPLE),
            ("top",   "เกรดที่พบบ่อยที่สุด", SUCCESS),
        ]
        for i, (key, label, color) in enumerate(specs):
            card = tk.Frame(wrap, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            wrap.grid_columnconfigure(i, weight=1)

            tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
            body = tk.Frame(card, bg=CARD_BG)
            body.pack(fill="both", expand=True, padx=14, pady=10)
            tk.Label(body, textvariable=self.stat_vars[key], bg=CARD_BG, fg=TEXT_DARK,
                     font=(FONT_NAME, 16, "bold")).pack(anchor="w")
            tk.Label(body, text=label, bg=CARD_BG, fg=TEXT_MUTED,
                     font=(FONT_NAME, 10)).pack(anchor="w")

    # ---------------- ตารางกรอกคะแนน ----------------
    def _build_table(self):
        outer = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        outer.pack(fill="both", expand=True, padx=28, pady=(0, 12))

        canvas = tk.Canvas(outer, bg=CARD_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                             style="Scroll.Vertical.TScrollbar")
        self.table_frame = tk.Frame(canvas, bg=CARD_BG)

        self.table_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        headers = ["#", "รหัสนักศึกษา", "ชื่อ-สกุล", "Midterm", "Final", "รวม", "เกรด"]
        widths  = [4, 13, 28, 9, 9, 8, 7]

        for c, (h, w) in enumerate(zip(headers, widths)):
            tk.Label(self.table_frame, text=h, width=w, bg=PRIMARY_DK, fg="white",
                     font=(FONT_NAME, 11, "bold"), pady=8
                     ).grid(row=0, column=c, sticky="nsew", padx=(1 if c else 0, 0))

        entry_kwargs = dict(font=(FONT_NAME, 11), relief="solid", bd=1, highlightthickness=0)

        for i in range(1, NUM_STUDENTS + 1):
            rowbg = CARD_BG if i % 2 else ROW_ALT

            no_lbl = tk.Label(self.table_frame, text=str(i), width=widths[0],
                               bg=rowbg, fg=TEXT_MUTED, font=(FONT_NAME, 11), pady=6)
            no_lbl.grid(row=i, column=0, sticky="nsew")

            id_entry = tk.Entry(self.table_frame, width=widths[1], justify="center", **entry_kwargs)
            id_entry.grid(row=i, column=1, sticky="nsew", padx=2, pady=2)

            name_entry = tk.Entry(self.table_frame, width=widths[2], **entry_kwargs)
            name_entry.grid(row=i, column=2, sticky="nsew", padx=2, pady=2)

            mid_entry = tk.Entry(self.table_frame, width=widths[3], justify="center", **entry_kwargs)
            mid_entry.grid(row=i, column=3, sticky="nsew", padx=2, pady=2)

            final_entry = tk.Entry(self.table_frame, width=widths[4], justify="center", **entry_kwargs)
            final_entry.grid(row=i, column=4, sticky="nsew", padx=2, pady=2)

            total_lbl = tk.Label(self.table_frame, text="-", width=widths[5],
                                  bg=rowbg, fg=TEXT_DARK, font=(FONT_NAME, 11), pady=6)
            total_lbl.grid(row=i, column=5, sticky="nsew")

            grade_lbl = tk.Label(self.table_frame, text="-", width=widths[6],
                                  bg=rowbg, fg=TEXT_MUTED, font=(FONT_NAME, 11, "bold"), pady=6)
            grade_lbl.grid(row=i, column=6, sticky="nsew")

            self.rows.append({
                "id": id_entry, "name": name_entry,
                "mid": mid_entry, "final": final_entry,
                "total_lbl": total_lbl, "grade_lbl": grade_lbl, "rowbg": rowbg,
            })

    # ---------------- แถบปุ่มด้านล่าง ----------------
    def _build_bottom_bar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=28, pady=(0, 20))

        ttk.Button(bar, text="✓  คำนวณคะแนน / เกรด", style="Primary.TButton",
                   command=self.calculate_all).pack(side="left", padx=(0, 8))
        ttk.Button(bar, text="⤓  บันทึกเป็น CSV", style="Info.TButton",
                   command=self.export_csv).pack(side="left", padx=8)
        ttk.Button(bar, text="↻  ล้างข้อมูลทั้งหมด", style="Danger.TButton",
                   command=self.clear_all).pack(side="left", padx=8)

    # ---------------- ฟังก์ชันการทำงาน ----------------
    def calculate_all(self):
        try:
            max_mid = float(self.max_mid_var.get())
            max_final = float(self.max_final_var.get())
            max_total = max_mid + max_final
            if max_total <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("ผิดพลาด", "กรุณากรอกคะแนนเต็ม Midterm/Final เป็นตัวเลขที่ถูกต้อง")
            return

        totals, valid_grades = [], []

        for row in self.rows:
            mid_txt = row["mid"].get().strip()
            final_txt = row["final"].get().strip()
            rowbg = row["rowbg"]

            if not mid_txt and not final_txt:
                row["total_lbl"].config(text="-")
                row["grade_lbl"].config(text="-", fg=TEXT_MUTED, bg=rowbg)
                continue

            try:
                mid = float(mid_txt) if mid_txt else 0.0
                final = float(final_txt) if final_txt else 0.0
            except ValueError:
                row["total_lbl"].config(text="ผิด")
                row["grade_lbl"].config(text="-", fg=DANGER, bg=rowbg)
                continue

            total = mid + final
            percent = (total / max_total) * 100
            grade = get_grade(percent)

            row["total_lbl"].config(text=f"{total:g}")
            row["grade_lbl"].config(text=grade, fg=GRADE_COLOR.get(grade, TEXT_DARK), bg=rowbg)

            totals.append(total)
            valid_grades.append(grade)

        if not valid_grades:
            messagebox.showwarning("แจ้งเตือน", "ยังไม่มีข้อมูลคะแนนให้คำนวณ")
            return

        avg_score = sum(totals) / len(totals)
        avg_gpa = sum(GRADE_POINT[g] for g in valid_grades) / len(valid_grades)
        top_grade = max(set(valid_grades), key=valid_grades.count)

        self.stat_vars["count"].set(f"{len(valid_grades)} / {NUM_STUDENTS}")
        self.stat_vars["avg"].set(f"{avg_score:.2f}")
        self.stat_vars["gpa"].set(f"{avg_gpa:.2f}")
        self.stat_vars["top"].set(top_grade)

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="grades_basic_computer_programming.csv",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["ลำดับ", "รหัสนักศึกษา", "ชื่อ-สกุล", "Midterm", "Final", "รวม", "เกรด"])
            for i, row in enumerate(self.rows, start=1):
                writer.writerow([
                    i, row["id"].get(), row["name"].get(),
                    row["mid"].get(), row["final"].get(),
                    row["total_lbl"].cget("text"), row["grade_lbl"].cget("text"),
                ])
        messagebox.showinfo("บันทึกสำเร็จ", f"บันทึกไฟล์ที่:\n{path}")

    def clear_all(self):
        if not messagebox.askyesno("ยืนยัน", "ต้องการล้างข้อมูลทั้งหมดหรือไม่?"):
            return
        for row in self.rows:
            row["id"].delete(0, tk.END)
            row["name"].delete(0, tk.END)
            row["mid"].delete(0, tk.END)
            row["final"].delete(0, tk.END)
            row["total_lbl"].config(text="-")
            row["grade_lbl"].config(text="-", fg=TEXT_MUTED, bg=row["rowbg"])
        for key, default in (("count", "0 / 20"), ("avg", "-"), ("gpa", "-"), ("top", "-")):
            self.stat_vars[key].set(default)


if __name__ == "__main__":
    app = GradeApp()
    app.mainloop()