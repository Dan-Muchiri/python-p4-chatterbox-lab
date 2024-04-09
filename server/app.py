from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'GET':
        # Fetch all messages ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()
        # Serialize the messages
        serialized_messages = [message.to_dict() for message in messages]
        # Return the serialized messages as JSON
        return jsonify(serialized_messages)
    elif request.method == 'POST':
        # Get data from request parameters
        data = request.json
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return jsonify({'error': 'Both body and username are required'}), 400

        # Create a new Message instance
        new_message = Message(body=body, username=username, created_at=datetime.utcnow(), updated_at=datetime.utcnow())

        # Add the new message to the database session
        db.session.add(new_message)
        # Commit changes to the database
        db.session.commit()

        # Return the newly created message as JSON
        return jsonify(new_message.to_dict()), 201
    
@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def message_by_id(id):
    message = Message.query.filter(Message.id == id).first()

    if message == None:
        response_body = {
            "message": "This record does not exist in our database. Please try again."
        }
        response = make_response(response_body, 404)

        return response

    else:
        if request.method == 'GET':
            message_dict = message.to_dict()

            response = make_response(
                message_dict,
                200
            )

            return response

        elif request.method == 'PATCH':
            # Update the message body if provided in the request JSON
            data = request.json
            body = data.get('body')
            if body:
                message.body = body
                # Update the 'updated_at' timestamp
                message.updated_at = datetime.utcnow()
                # Commit changes to the database
                db.session.commit()
            
            # Fetch the updated message from the database
            updated_message = Message.query.get_or_404(id)
            # Return the updated message as JSON
            return jsonify(updated_message.to_dict())

        elif request.method == 'DELETE':
            db.session.delete(message)
            db.session.commit()

            response_body = {
                "delete_successful": True,
                "message": "Message deleted."
            }

            response = make_response(
                response_body,
                200
            )

            return response


if __name__ == '__main__':
    app.run(port=5555)
