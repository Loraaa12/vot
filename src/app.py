from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from minio import Minio
from minio.error import S3Error
import io
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
jwt = JWTManager(app)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MinIO client setup
minio_client = Minio(
    "localhost:9000",  # MinIO server address
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

BUCKET_NAME = "file-storage"

# Ensure the bucket exists
if not minio_client.bucket_exists(BUCKET_NAME):
    logger.info(f"Creating bucket: {BUCKET_NAME}")
    minio_client.make_bucket(BUCKET_NAME)
else:
    logger.info(f"Bucket {BUCKET_NAME} already exists")


# Role-based access control decorator
def has_role(required_role):
    def wrapper(fn):
        def decorator(*args, **kwargs):
            # Get the current user's roles from the JWT
            identity = get_jwt_identity()
            user_roles = identity.get("roles", [])
            if required_role not in user_roles:
                logger.warning(f"Unauthorized access attempt by user with roles: {user_roles}")
                return jsonify(msg="You don't have permission to access this resource"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


# Authentication endpoint for testing
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    if username == "testuser" and password == "password123":  # Replace with Keycloak integration later
        # Assign roles to the user
        roles = ["uchenici"]  # Assign 'uchenici' role
        token = create_access_token(identity={"username": username, "roles": roles})
        logger.info(f"User {username} logged in successfully")
        return jsonify(access_token=token), 200
    logger.warning(f"Failed login attempt with username: {username}")
    return jsonify({"msg": "Invalid credentials"}), 401


# Upload endpoint (restricted to non-'uchenici' roles)
@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    identity = get_jwt_identity()
    user_roles = identity.get("roles", [])
    
    # If the user is 'uchenici', they are not allowed to upload
    if "uchenici" in user_roles:
        logger.warning(f"Upload attempt by restricted role: {user_roles}")
        return jsonify({"msg": "You don't have permission to upload files"}), 403

    if 'file' not in request.files:
        logger.error("No file provided for upload")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    try:
        minio_client.put_object(
            BUCKET_NAME, file.filename, file.stream, length=-1, part_size=10 * 1024 * 1024
        )
        logger.info(f"File '{file.filename}' uploaded successfully")
        return jsonify({"message": f"File '{file.filename}' uploaded successfully"}), 200
    except S3Error as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Download endpoint (allowed for 'uchenici' role)
@app.route('/download/<file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    try:
        file_data = minio_client.get_object(BUCKET_NAME, file_id)
        logger.info(f"File '{file_id}' downloaded successfully")
        return send_file(
            io.BytesIO(file_data.read()),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=file_id
        )
    except S3Error as e:
        logger.error(f"Error downloading file '{file_id}': {str(e)}")
        return jsonify({"error": str(e)}), 404


# Update endpoint (restricted to non-'uchenici' roles)
@app.route('/update/<file_id>', methods=['PUT'])
@jwt_required()
def update_file(file_id):
    identity = get_jwt_identity()
    user_roles = identity.get("roles", [])
    
    # If the user is 'uchenici', they are not allowed to update
    if "uchenici" in user_roles:
        logger.warning(f"Update attempt by restricted role: {user_roles}")
        return jsonify({"msg": "You don't have permission to update files"}), 403

    if 'file' not in request.files:
        logger.error("No file provided for update")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    try:
        # Delete the existing file
        minio_client.remove_object(BUCKET_NAME, file_id)
        # Upload the new file
        minio_client.put_object(
            BUCKET_NAME, file_id, file.stream, length=-1, part_size=10 * 1024 * 1024
        )
        logger.info(f"File '{file_id}' updated successfully")
        return jsonify({"message": f"File '{file_id}' updated successfully"}), 200
    except S3Error as e:
        logger.error(f"Error updating file '{file_id}': {str(e)}")
        return jsonify({"error": str(e)}), 500


# Delete endpoint (restricted to non-'uchenici' roles)
@app.route('/delete/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    identity = get_jwt_identity()
    user_roles = identity.get("roles", [])
    
    # If the user is 'uchenici', they are not allowed to delete
    if "uchenici" in user_roles:
        logger.warning(f"Delete attempt by restricted role: {user_roles}")
        return jsonify({"msg": "You don't have permission to delete files"}), 403

    try:
        minio_client.remove_object(BUCKET_NAME, file_id)
        logger.info(f"File '{file_id}' deleted successfully")
        return jsonify({"message": f"File '{file_id}' deleted successfully"}), 200
    except S3Error as e:
        logger.error(f"Error deleting file '{file_id}': {str(e)}")
        return jsonify({"error": str(e)}), 404


if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000)
