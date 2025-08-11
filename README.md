
````markdown
# 🛡️ Phishing Email Detector (Local, Tkinter, Regex/NLP)

A clean, local-only phishing email detector with a login screen, Tkinter GUI, NLP-enhanced detection, risk meter, and local scan history. No external APIs required—runs entirely offline.

---

## 🚀 Features

- ✅ Local-only detection (no external APIs)  
- 🔍 Regex URL scanning + keyword/phrase matching  
- 🧠 NLP sentence analysis with NLTK (auto-fallback if missing)  
- 📊 Risk score (0–100) and levels: Low / Medium / High  
- 🖼️ GUI with progress bar, sample emails, copy & save report  
- 📁 Scan history saved locally to `data/history.json`  

---

## 🧰 Requirements

- Python 3.9 or higher (tested up to Python 3.13)  
- [Optional] NLTK (`punkt` is auto-downloaded if missing)  

### ✅ Install NLTK (Recommended)

```bash
pip install nltk
````

To manually download sentence tokenizer:

```python
import nltk
nltk.download('punkt')
```

Or just run the app — it attempts to download quietly on its own.

---

## 🧪 How to Run

From the project root:

```bash
python main.py
```

---

## 🔐 Login credentials

* Username: `admin`
* Password: `1234`

---

## 📌 Folder Structure

```
phishing_detector/
│
├── assets/
│   └── logo.png                  # Optional
│
├── data/
│   ├── suspicious_keywords.txt   # List of phishing keywords
│   ├── samples.json              # Prefilled email examples
│   └── history.json              # Auto-saved scan logs
│
├── src/
│   ├── __init__.py
│   ├── utils.py                  # Regex, URL scanner, NLTK setup
│   ├── detector.py               # Detection logic + scoring
│   ├── login.py                  # Login UI
│   └── gui.py                    # GUI and result display
│
├── main.py                       # Entry launcher
└── README.md                     # Documentation
```

---

## 🛠️ Troubleshooting

### 🔍 Issue: punkt not found

If you see:

```
LookupError: Resource 'punkt' not found
```

Fix it by running:

```python
import nltk
nltk.download('punkt')
```

Or re-run the app — it tries to fix it automatically.

---

## 🧱 Customization Tips

* Add or edit keywords in `data/suspicious_keywords.txt`
* Add more sample emails to `data/samples.json`
* Scan report saved to: `./reports/scan_report.txt`
* History of scans saved to: `data/history.json`

UI and logic are modular — you can easily add:

* Dark mode
* User registration/login
* File/email attachment scanner
* Export as PDF

---

## 📃 Quick Setup Summary

1. Create folder structure exactly as shown above.
2. Add code to each file (`main.py`, `src/*.py`, `data/*.txt/json`)
3. \[Optional] Install NLTK:

```bash
pip install nltk
```

4. Run the app:

```bash
python main.py
```

5. Log in as `admin` / `1234`, test samples, scan emails, save reports.

---

Enjoy your local phishing email detector! 🛡️🚫📧

```
