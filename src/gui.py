import json
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path

from src.detector import detect_phishing
from src.utils import data_path, append_history


def show_main_gui(root: tk.Tk):
    # Clear previous widgets (e.g., login)
    for w in root.winfo_children():
        w.destroy()

    root.title("Phishing Email Detector")
    root.geometry("900x650")

    # ---------- Styles ----------
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("TButton", padding=8)
    style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
    style.configure("Sub.TLabel", font=("Segoe UI", 11))

    # ---------- Main container ----------
    container = ttk.Frame(root, padding=16)
    container.pack(fill="both", expand=True)

    # Use grid so the action row stays visible; only text areas expand
    container.columnconfigure(0, weight=1)
    # Rows 3 and 5 (the two ScrolledText areas) will expand
    for r in (3, 5):
        container.rowconfigure(r, weight=1)

    # Row 0: Header
    header = ttk.Label(container, text="Phishing Email Scanner", style="Header.TLabel")
    header.grid(row=0, column=0, sticky="w")

    # Row 1: Subtitle
    sub = ttk.Label(
        container,
        text="Paste or type an email below, or load a sample. Click Scan to analyze.",
        style="Sub.TLabel",
    )
    sub.grid(row=1, column=0, sticky="w", pady=(2, 10))

    # Row 2: Controls (samples, load, clear)
    controls = ttk.Frame(container)
    controls.grid(row=2, column=0, sticky="we", pady=(0, 8))
    controls.columnconfigure(3, weight=1)  # spacer to push buttons left if window is wide

    samples = _load_samples()
    sample_titles = [s["title"] for s in samples] if samples else []
    sample_var = tk.StringVar(value=sample_titles[0] if sample_titles else "")

    ttk.Label(controls, text="Sample:").grid(row=0, column=0, padx=(0, 8))
    sample_cb_state = "readonly" if sample_titles else "disabled"
    sample_cb = ttk.Combobox(
        controls,
        textvariable=sample_var,
        values=sample_titles,
        state=sample_cb_state,
        width=32,
    )
    sample_cb.grid(row=0, column=1, padx=(0, 6))

    # Email input (created before handler so handler can reference it)
    email_label = ttk.Label(container, text="Email content:")

    email_text_box = ScrolledText(container, height=14, font=("Consolas", 10), wrap="word")

    def load_selected_sample():
        if not samples:
            return
        title = sample_var.get()
        body = next((s["body"] for s in samples if s["title"] == title), "")
        if body:
            email_text_box.delete("1.0", tk.END)
            email_text_box.insert("1.0", body)

    ttk.Button(controls, text="Load Sample", command=load_selected_sample, state=("normal" if samples else "disabled")).grid(
        row=0, column=2, padx=6
    )
    ttk.Button(controls, text="Clear", command=lambda: _clear(email_text_box, result_box=None)).grid(
        row=0, column=4, padx=6
    )

    # Row 3: Email label + text box
    email_label.grid(row=3, column=0, sticky="w", pady=(4, 4))
    email_text_box.grid(row=4, column=0, sticky="nsew")  # this row will expand (rowconfigure set above)

    # Prefill with first sample or a default message
    if samples:
        email_text_box.insert("1.0", samples[0]["body"])
    else:
        email_text_box.insert(
            "1.0",
            "Dear Customer,\n\nWe’ve detected suspicious activity on your account. "
            "Please verify your information immediately:\n\nhttp://secure-login-update.com\n\n"
            "Failure to act may result in temporary suspension.\n\nThank you,\nSecurity Team",
        )

    # Row 5: Result header (left) + risk meter (right)
    result_header = ttk.Frame(container)
    result_header.grid(row=5, column=0, sticky="we", pady=(12, 4))
    result_header.columnconfigure(0, weight=1)

    ttk.Label(result_header, text="Scan result:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")

    meter_frame = ttk.Frame(result_header)
    meter_frame.grid(row=0, column=1, sticky="e")
    ttk.Label(meter_frame, text="Risk:").pack(side="left", padx=(0, 6))
    risk_var = tk.IntVar(value=0)
    meter = ttk.Progressbar(
        meter_frame, orient="horizontal", length=220, mode="determinate", maximum=100, variable=risk_var
    )
    meter.pack(side="left")

    # Row 6: Result box (expands)
    result_box = ScrolledText(container, height=10, font=("Consolas", 10), wrap="word", state="disabled")
    result_box.grid(row=6, column=0, sticky="nsew")

    # Row 7: Actions (Scan, Copy, Save) — always visible
    actions = ttk.Frame(container)
    actions.grid(row=7, column=0, sticky="we", pady=(8, 0))
    actions.columnconfigure(3, weight=1)  # spacer

    scan_btn = ttk.Button(
        actions,
        text="Scan Email",
        command=lambda: _scan(email_text_box, result_box, risk_var),
    )
    scan_btn.grid(row=0, column=0)

    ttk.Button(actions, text="Copy Result", command=lambda: _copy_to_clipboard(root, result_box)).grid(
        row=0, column=1, padx=8
    )
    ttk.Button(actions, text="Save Report", command=lambda: _save_report(result_box)).grid(
        row=0, column=2
    )


def _load_samples():
    p = data_path("samples.json")
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _clear(email_box: ScrolledText, result_box: ScrolledText | None):
    email_box.delete("1.0", tk.END)
    if result_box is not None:
        result_box.configure(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.configure(state="disabled")


def _scan(email_box: ScrolledText, result_box: ScrolledText, risk_var: tk.IntVar):
    email_text = email_box.get("1.0", tk.END).strip()
    if not email_text:
        messagebox.showwarning("No content", "Please enter or load an email to scan.")
        return

    result = detect_phishing(email_text)

    # Update risk meter
    risk_var.set(result.score)

    # Build output text
    lines = []
    lines.append(f"Summary: {result.risk_level} risk ({result.score}/100)")
    lines.append("")
    if result.flagged_keywords:
        lines.append("Keywords detected:")
        for kw in result.flagged_keywords:
            lines.append(f"  - {kw}")
        lines.append("")
    if result.suspicious_urls:
        lines.append("Suspicious URLs:")
        for u in result.suspicious_urls:
            lines.append(f"  - {u}")
        lines.append("")
    if result.suspicious_sentences:
        lines.append("Suspicious sentences:")
        for s in result.suspicious_sentences:
            lines.append(f"  - {s}")
        lines.append("")
    # Details
    lines.append("Details:")
    for k, v in result.details.items():
        lines.append(f"  - {k}: {v}")

    output = "\n".join(lines)

    # Show in result box
    result_box.configure(state="normal")
    result_box.delete("1.0", tk.END)
    result_box.insert("1.0", output)
    result_box.configure(state="disabled")

    # Save to history
    try:
        append_history({
            "summary": {"risk_level": result.risk_level, "score": result.score},
            "keywords": result.flagged_keywords,
            "urls": result.suspicious_urls,
            "sentences": result.suspicious_sentences,
            "details": result.details,
            "preview": email_text[:240] + ("..." if len(email_text) > 240 else ""),
        })
    except Exception:
        # Non-fatal if history can't be saved
        pass


def _copy_to_clipboard(root: tk.Tk, result_box: ScrolledText):
    text = result_box.get("1.0", tk.END).strip()
    if not text:
        return
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Copied", "Result copied to clipboard.")


def _save_report(result_box: ScrolledText):
    text = result_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Nothing to save", "Please run a scan before saving.")
        return
    reports_dir = Path.cwd() / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / "scan_report.txt"
    try:
        report_path.write_text(text, encoding="utf-8")
        messagebox.showinfo("Saved", f"Report saved to: {report_path}")
    except Exception as e:
        messagebox.showerror("Save failed", str(e))
