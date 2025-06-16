import sqlite3
import uuid
from datetime import datetime
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="Your_Key")  # Replace with your key

# Initialize SQLite database
conn = sqlite3.connect("complaints.db")
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

# Knowledge base
knowledge_base = {
    "delayed delivery": "If your delivery is delayed by more than 7 days, you may be eligible for a full refund.",
    "refund policy": "Our refund policy allows you to request a return within 30 days of purchase, provided the item is unused.",
    "warranty": "All electronics come with a one-year warranty from the date of delivery."
}

def generate_response(prompt):
    """
    Generate a response using OpenAI's API.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def create_complaint(data):
    """
    Create a complaint in the database.
    """
    complaint_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO complaints (complaint_id, name, phone, email, complaint_details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (complaint_id, data["name"], data["phone"], data["email"], data["complaint_details"], timestamp))
    conn.commit()
    return complaint_id

def get_complaint(complaint_id):
    """
    Retrieve a complaint from the database by ID.
    """
    cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
    row = cursor.fetchone()
    if row:
        return {
            "complaint_id": row[0],
            "name": row[1],
            "phone": row[2],
            "email": row[3],
            "complaint_details": row[4],
            "created_at": row[5]
        }
    return None

def chat():
    """
    Interactive chatbot interface in the terminal.
    """
    print("\nWelcome to the Complaint Chatbot. Type 'exit' to quit.")
    conversation_state = {"name": "", "phone": "", "email": "", "complaint_details": ""}
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        # Check for complaint status requests
        if "status" in user_input.lower() or "complaint id" in user_input.lower():
            words = user_input.split()
            complaint_id = next((word for word in words if len(word) == 8), None)
            if complaint_id:
                complaint = get_complaint(complaint_id)
                if complaint:
                    print(f"\nComplaint ID: {complaint['complaint_id']}")
                    print(f"Name: {complaint['name']}")
                    print(f"Phone: {complaint['phone']}")
                    print(f"Email: {complaint['email']}")
                    print(f"Details: {complaint['complaint_details']}")
                    print(f"Created At: {complaint['created_at']}")
                else:
                    print("Sorry, no complaint found with that ID.")
            else:
                print("Please provide a valid complaint ID.")
            continue

        # Check the knowledge base
        for keyword, response in knowledge_base.items():
            if keyword in user_input.lower():
                print(f"Bot: {response}")
                break
        else:
            # Generate response using OpenAI if no match in knowledge base
            ai_response = generate_response(user_input)
            print(f"Bot: {ai_response}")

            # Handle complaint registration if relevant
            if "complaint" in user_input.lower() or "register" in user_input.lower():
                if not conversation_state["name"]:
                    conversation_state["name"] = input("Bot: What's your name? ").strip()
                if not conversation_state["phone"]:
                    conversation_state["phone"] = input("Bot: Your phone number? ").strip()
                if not conversation_state["email"]:
                    conversation_state["email"] = input("Bot: Your email address? ").strip()
                if not conversation_state["complaint_details"]:
                    conversation_state["complaint_details"] = user_input

                if all(conversation_state.values()):
                    complaint_id = create_complaint(conversation_state)
                    print(f"\nBot: Your complaint has been registered with ID: {complaint_id}")
                    # Reset for next complaint
                    conversation_state = {"name": "", "phone": "", "email": "", "complaint_details": ""}
                else:
                    print("Bot: I'm collecting your complaint information...")

if __name__ == "__main__":
    chat()
1
