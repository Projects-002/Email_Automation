import imaplib
import email
from email.header import decode_header
import csv

def read_email(username, password):
    emails = []
    try:
        # Connect to the Gmail IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")

        # Search for all emails in the inbox
        _, messages = mail.search(None, "ALL")

        email_ids = messages[0].split()[:20]  # Fetch only the first five emails
        for email_id in email_ids:
            # Fetch the email by ID
            _, msg_data = mail.fetch(email_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    from_ = msg.get("From")
                    email_data = {
                        "subject": subject,
                        "from": from_,
                        "body": ""
                    }
                    
                    # Check if the email message is multipart
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_disposition = str(part.get("Content-Disposition"))
                            if "attachment" not in content_disposition:
                                content_type = part.get_content_type()
                                
                                # Check for text or html content and decode accordingly
                                if content_type == "text/plain":
                                    body = part.get_payload(decode=True).decode(encoding if encoding else "utf-8", errors="ignore")
                                    email_data["body"] = body[:500]  # Store a truncated version
                                elif content_type == "text/html":
                                    html_body = part.get_payload(decode=True).decode(encoding if encoding else "utf-8", errors="ignore")
                                    email_data["body"] = html_body[:500]  # Store truncated HTML content
                    else:
                        body = msg.get_payload(decode=True).decode(encoding if encoding else "utf-8", errors="ignore")
                        email_data["body"] = body[:500]  # Store a truncated version

                    emails.append(email_data)

        mail.logout()

        # Write the emails to a CSV file
        with open("emails.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["subject", "from", "body"])
            writer.writeheader()
            writer.writerows(emails)

    except Exception as e:
        print(f"An error occurred: {e}")

# Use Gmail app password for authentication if 2FA is enabled
username = "khansamuel58@gmail.com"
password = "rwinogbszsfwdpnw"

# Call the function to read emails
read_email(username, password)
# Output: emails.csv file containing email data
