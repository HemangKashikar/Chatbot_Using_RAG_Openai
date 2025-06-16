from flask import Flask, request, jsonify
import sqlite3
import uuid
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key="key") 
def get_db():
    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row
    return conn
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        complaint_details TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()
knowledge_base = {
    "delayed delivery": "If your delivery is delayed by more than 7 days, you may be eligible for a full refund.",
    "refund policy": "Our refund policy allows you to request a return within 30 days of purchase, provided the item is unused.",
    "warranty": "All electronics come with a one-year warranty from the date of delivery."
}

def generate_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()
@app.route("/complaints", methods=["POST"])
def create_complaint():
    data = request.get_json()
    required = ["name", "phone", "email", "complaint_details"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    complaint_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO complaints (complaint_id, name, phone, email, complaint_details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            complaint_id, data["name"], data["phone"], data["email"], data["complaint_details"], timestamp
        ))
        conn.commit()

    return jsonify({"message": "Complaint registered", "complaint_id": complaint_id})
@app.route("/complaints/<complaint_id>", methods=["GET"])
def get_complaint(complaint_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
        row = cursor.fetchone()
        if row:
            return jsonify(dict(row))
        else:
            return jsonify({"error": "Complaint not found"}), 404
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").lower()

    if not user_input:
        return jsonify({"error": "Message is required"}), 400
    for keyword, answer in knowledge_base.items():
        if keyword in user_input:
            return jsonify({"response": answer})
    try:
        ai_response = generate_response(user_input)
        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True)
