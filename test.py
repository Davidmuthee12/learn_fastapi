from app.worker.tasks import send_mail

# send_mail(
#     recipients=["apfg54@goxok.com"],
#     subject="Test mailcoming through once",
#     body="Nothing funny here mate...",
# )

result = send_mail.delay(
    recipients=["apfg54@goxok.com"],
    subject="Test mailcoming through once",
    body="Nothing funny here mate...",
)

result.status

result.get()
