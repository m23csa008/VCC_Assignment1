from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# SQLite for now; we'll switch to PostgreSQL/MySQL on Ubuntu VMs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Message Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(255), nullable=False)

# Create DB Tables
with app.app_context():
    db.create_all()

# # Send Message
# @app.route('/send_message', methods=['POST'])
# def send_message():
#     data = request.json
#     new_message = Message(sender=data['sender'], receiver=data['receiver'], content=data['content'])
    
#     db.session.add(new_message)
#     db.session.commit()
    
#     return jsonify({'message': 'Message sent successfully'}), 201


AUTH_SERVICE_URL = "http://192.168.56.101:5000"  # Change to VM1 IP

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    
    # Verify sender exists using VM1 Auth Service
    response = requests.get(f"{AUTH_SERVICE_URL}/users")
    users = response.json()
    
    if not any(user['username'] == data['sender'] for user in users):
        return jsonify({'message': 'Sender not found'}), 400

    # Store message in the database
    new_message = Message(sender=data['sender'], receiver=data['receiver'], content=data['content'])
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({'message': 'Message sent successfully'}), 201


# Get Messages for a User
@app.route('/get_messages/<username>', methods=['GET'])
def get_messages(username):
    messages = Message.query.filter((Message.sender == username) | (Message.receiver == username)).all()
    return jsonify([{'sender': msg.sender, 'receiver': msg.receiver, 'content': msg.content} for msg in messages])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
