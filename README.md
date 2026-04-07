# Apartment Management System

A web-based management application built for apartment building managers to handle dues tracking, expense management, reporting, and communication — all from a single dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-DB-003B57?logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

### Dashboard
- Annual income, expenses, cash balance, and monthly dues summary cards
- Annual and current collection rate percentages
- Unpaid dues warning list (which apartment, which month)
- Quick access links to all modules

### Payment Tracking
- Monthly payment status view for 12 apartments
- One-click paid/unpaid toggle (real-time update via HTMX)
- Bulk payment: mark multiple months as paid for a single apartment at once
- Apartment detail page: yearly payment history, total debt, overdue months
- Per-apartment PDF report download

### Expense Management
- Monthly expense recording (category, amount, description)
- Pre-defined expense categories: Electricity, Water, Cleaning, Elevator Maintenance
- Add custom expense categories, activate/deactivate as needed
- Automatic cash register update on expense changes

### Cash Register
- Annual income / expense / balance summary
- Month-to-month carryover calculation
- Expense distribution by category (with percentages)
- Collection rate tracking

### Message Preparation
- Auto-generate reminder messages for apartments with unpaid dues
- General announcement message creation
- Template support: `{apartman_adi}`, `{ay_yil}`, `{miktar}`, `{odemeyenler}`
- Message preview and copy to clipboard

### Reports (Excel + PDF)
- **Monthly Summary:** Income, expenses, net, expense breakdown
- **Payment Status:** All apartments with paid/unpaid status (color-coded)
- **Expense Detail:** Per-category amounts and percentages
- **Annual Summary:** 12-month income/expense/net table
- Turkish character support, professional table styling

### Notes
- Separate note area for each month
- Create, edit, and delete notes
- Visual indicator showing which months have notes
- Last update timestamp

### Directory
- **Staff:** Elevator technician, cleaner, etc. (name, phone, IBAN)
- **Subscriptions:** Electricity, water, natural gas (subscriber/meter number)
- **Building Info:** Address, general information, phone, IBAN

### Activity Logs
- Automatic logging of all operations
- Search and filter functionality
- Pagination (50 records per page)

### Settings
- Edit building name
- Change monthly dues amount (with rate change history)
- Update apartment resident info (name, phone)
- Expense category management
- Message template editing
- Database backup (download / list backups)
- Full data reset (with confirmation code)

### Email Notifications
- SMTP-based email sending
- Automatic dues reminder on the first Monday of each month
- Notification status tracking

### Responsive Design
- Hamburger menu with slide-out sidebar on mobile
- Cards, tables, and forms adapt to mobile screens
- Clean layout on phone, tablet, and desktop

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.1, Flask-SQLAlchemy |
| Database | SQLite |
| Frontend | Bootstrap 5.3, Bootstrap Icons, HTMX 2.0 |
| Reporting | ReportLab (PDF), OpenPyXL (Excel) |
| Fonts | Plus Jakarta Sans, JetBrains Mono |
| Theme | Dark Theme |

---

## Installation

### Requirements
- Python 3.10 or higher
- pip

### Steps

```bash
# Clone the repository
git clone https://github.com/enes-ak/apartment-management.git
cd apartment-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open `http://localhost:5000` in your browser.

> **Note:** The database and 12 apartments are automatically created on first run.

---

## Project Structure

```
apartment-management/
├── app.py                  # Application entry point
├── config.py               # Configuration
├── database.py             # Database initialization
├── requirements.txt        # Python dependencies
│
├── models/                 # Database models
│   ├── daire.py            # Apartment unit
│   ├── odeme.py            # Payment tracking
│   ├── gider.py            # Expenses & expense categories
│   ├── kasa.py             # Cash register (income/expense summary)
│   ├── ayar.py             # Settings, dues config, notifications
│   ├── log.py              # Activity logs
│   ├── not_.py             # Monthly notes
│   └── rehber.py           # Directory (staff/subscriptions/info)
│
├── routes/                 # URL routes
│   ├── ana_sayfa.py        # Dashboard
│   ├── odemeler.py         # Payment operations
│   ├── giderler.py         # Expense operations
│   ├── kasa.py             # Cash register view
│   ├── mesajlar.py         # Message preparation
│   ├── raporlar.py         # Report downloads
│   ├── notlar.py           # Note management
│   ├── rehber.py           # Directory management
│   ├── loglar.py           # Log viewing
│   └── ayarlar.py          # Settings management
│
├── services/               # Business logic services
│   ├── kasa_servisi.py     # Cash register calculations
│   ├── rapor_servisi.py    # Excel & PDF report generation
│   └── mail_servisi.py     # Email sending
│
├── templates/              # HTML templates (Jinja2)
│   ├── base.html           # Main layout (sidebar, responsive)
│   ├── ana_sayfa.html      # Dashboard
│   ├── odemeler.html       # Payment table
│   ├── daire_detay.html    # Apartment detail page
│   ├── giderler.html       # Expense recording
│   ├── kasa.html           # Cash register summary
│   ├── mesajlar.html       # Message preparation
│   ├── raporlar.html       # Report selection
│   ├── notlar.html         # Monthly notes
│   ├── rehber.html         # Directory
│   ├── loglar.html         # Log list
│   ├── ayarlar.html        # Settings
│   └── parcalar/           # Reusable partials
│       ├── odeme_satir.html
│       └── mesaj_onizleme.html
│
├── static/
│   ├── css/stil.css        # All styles (dark theme + responsive)
│   ├── js/uygulama.js      # JavaScript utilities
│   └── favicon.svg         # Favicon
│
├── tests/                  # Test files
│   ├── test_modeller.py
│   ├── test_odemeler.py
│   ├── test_giderler.py
│   ├── test_kasa.py
│   ├── test_raporlar.py
│   ├── test_mesajlar.py
│   ├── test_mail.py
│   └── test_ayarlar.py
│
├── raporlar/               # Generated reports (gitignored)
└── yedekler/               # Database backups (gitignored)
```

---

## Tests

```bash
pytest
```

---

## License

MIT
