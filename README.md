# 🎓 College Data Manager

A Python desktop application to store, manage, and filter detailed information about Indian colleges — built with `tkinter` for the UI and `SQLite` for persistent local storage.

---

## 📌 Description

College Data Manager is a standalone desktop tool designed to help students, counselors, and researchers organize and explore college data in one place. Instead of juggling spreadsheets or multiple websites, you can store every college's key details locally and instantly filter them by any criteria — state, ranking, package, admission mode, and more.

The app comes pre-loaded with 10 sample colleges (IITs, NITs, BITS, IIM, etc.) so you can explore it right away, and you can add, edit, or delete records at any time.

---

## ✨ Features

- **Add / Edit / Delete** college records through a clean form dialog
- **Filter** colleges by:
  - College Name
  - State
  - Admission Mode (JEE Advanced, CAT, BITSAT, etc.)
  - NIRF Ranking (upper limit)
  - Placement Percentage (lower limit)
  - Average Package (lower limit)
- **Sort** any column by clicking the table header
- **Live stats bar** showing total colleges, states covered, avg NIRF rank, avg package
- **Persistent storage** — all data saved locally in a SQLite database (`colleges.db`)
- **10 sample colleges** seeded on first launch

---

## 📋 Data Fields

| Field | Description |
|---|---|
| College ID | Unique identifier (e.g. IIT001) |
| College Name | Full name of the institution |
| NIRF Ranking | National ranking by NIRF |
| State | State where the college is located |
| State Ranking | Rank within the state |
| Placement % | Percentage of students placed |
| Campus Size | Area of campus in acres |
| Avg Package | Average CTC offered (₹ Lakhs) |
| Highest Package | Highest CTC offered (₹ Crores) |
| Placement Year | Year the placement data is from |
| Year Established | Year the college was founded |
| Admission Mode | Entrance exam / mode of admission |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x (tkinter is included in the standard library)
- No additional packages required

### Run

```bash
git clone https://github.com/YOUR_USERNAME/college-data-manager.git
cd college-data-manager
python college_app.py
```

The app will automatically create a `colleges.db` file in the same directory on first run and seed it with sample data.

---

## 🗂 Project Structure

```
college-data-manager/
├── college_app.py   # Main application (UI + DB logic)
├── colleges.db      # Auto-generated SQLite database (gitignored)
└── README.md
```

> **Tip:** Add `colleges.db` to your `.gitignore` if you don't want to commit your local data.

---

## 🛠 Built With

- **Python 3** — core language
- **tkinter** — desktop GUI (built into Python)
- **SQLite3** — local database (built into Python)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
