# app.py
from flask import Flask, render_template, request, redirect, url_for
import base64, uuid, time
import pdf417
import os
from PIL import Image

app = Flask(__name__)
TICKET_STORE = {}  # short_id -> {token, info, timestamp}

def generate_short_id():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()[:8]

@app.route("/")
def form():
    return render_template("form.html")

@app.route("/generate", methods=["POST"])
def generate():
    token = request.form["token"]
    event_name = request.form["event"]
    section = request.form["section"]
    row = request.form["row"]
    seat = request.form["seat"]

    short_id = generate_short_id()
    TICKET_STORE[short_id] = {
        "token": token,
        "event": event_name,
        "section": section,
        "row": row,
        "seat": seat,
        "created": time.time()
    }
    return redirect(url_for("ticket", ticket_id=short_id))

@app.route("/ticket/<ticket_id>")
def ticket(ticket_id):
    ticket = TICKET_STORE.get(ticket_id)
    if not ticket:
        return "Ticket not found", 404
    return render_template("ticket.html", ticket=ticket, ticket_id=ticket_id)

@app.route("/barcode/<ticket_id>")
def barcode(ticket_id):
    ticket = TICKET_STORE.get(ticket_id)
    if not ticket:
        return "Not found", 404
    raw = ticket["token"]
    codes = pdf417.encode(raw, columns=6, security_level=5)
    image = pdf417.render_image(codes)
    path = f"static/barcodes/{ticket_id}.png"
    os.makedirs("static/barcodes", exist_ok=True)
    image.save(path)
    return redirect(f"/{path}?t={int(time.time())}")

if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
