import os
import smtplib
from email.mime.text import MIMEText
from health_check import results

# -----------------------------
# Environment Variables
# -----------------------------
EMAIL = os.getenv("REPORT_EMAIL")
PASSWORD = os.getenv("REPORT_EMAIL_PASSWORD")

# IMPORTANT: use nginx service inside docker network
BASE_URL = os.getenv("API_BASE_URL", "http://nginx")


# -----------------------------
# Generate Report
# -----------------------------
def generate_report():
    success = sum(1 for r in results if r.get("success"))
    total = len(results)

    report = f"""
Pricing AI - API Health Report

Base URL: {BASE_URL}

Total APIs tested: {total}
Successful: {success}
Failed: {total - success}

Details:
"""

    for r in results:
        report += f"\n{r}"

    return report


# -----------------------------
# Send Email
# -----------------------------
def send_email():
    if not EMAIL or not PASSWORD:
        raise ValueError(
            "Missing REPORT_EMAIL or REPORT_EMAIL_PASSWORD env variables"
        )

    msg = MIMEText(generate_report())
    msg["Subject"] = "Pricing AI - Daily API Health Report"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

    print(" Health report email sent successfully.")


# -----------------------------
# Run Script
# -----------------------------
if __name__ == "__main__":
    print("Running API health report...")
    send_email()