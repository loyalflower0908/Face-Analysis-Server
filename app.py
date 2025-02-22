from flask import Flask, request, jsonify
import os
import time
from face_analysis import analyze_face
from face_analysis_server.generate_random_string import generate_random_string

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 유저 및 인증 정보 저장
user_data = {}  # { "user_id": { "password": "XXXXXX", "token": "YYYYYY" } }
user_analysis = {}  # { "user_id": { "gender": 1, "age": 26, "emotion": 4 } }


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '이미지 파일  오류'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': '파일이 존재하지 않습니다'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 얼굴 분석 수행
    analysis_result = analyze_face(filepath)

    # 얼굴이 감지되지 않으면 400 오류 반환
    if not analysis_result or ("error" in analysis_result and analysis_result["error"] == "No face detected"):
        print("얼굴 인식 안됨")
        return jsonify({'error': '얼굴이 인식되지 않았습니다'}), 400

    # 랜덤 사용자 ID, 비밀번호 생성
    user_id = generate_random_string(12)
    password = generate_random_string(8)

    # 유저별 분석 데이터 저장
    user_analysis[user_id] = analysis_result

    # 저장된 유저 정보에 추가
    user_data[user_id] = {"password": password, "token": None}

    return jsonify({
        "id": user_id,
        "pw": password
    }), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'user_id' not in data or 'password' not in data:
        return jsonify({'error': 'Missing userId or password'}), 400

    user_id = data['user_id']
    password = data['password']

    if user_id in user_data and user_data[user_id]["password"] == password:
        # 랜덤 토큰 생성 및 저장
        token = generate_random_string(32)
        user_data[user_id]["token"] = token

        return jsonify({
            "token": token,
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/<user_id>/attributes', methods=['GET'])
def get_user_attributes(user_id):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'error': 'Missing or invalid Authorization header'}), 401

    token = auth_header.split("Bearer ")[1]

    # 유효한 사용자 ID인지 확인
    if user_id not in user_data:
        return jsonify({'error': 'User not found'}), 404

    # 토큰이 유효한지 확인
    if user_data[user_id]["token"] is None or user_data[user_id]["token"] != token:
        return jsonify({'error': 'Invalid token'}), 403

    # 현재 시간을 Unix Timestamp (밀리초 단위)로 변환
    current_timestamp = int(time.time() * 1000)

    # 해당 사용자의 분석 데이터를 가져옴
    user_attributes = user_analysis.get(user_id, {"gender": "오류", "age": "오류", "emotion": "오류", "race": "오류"})

    attributes = [
        {"lastUpdateTs": current_timestamp, "key": "gender", "value": user_attributes.get("gender", "오류")},
        {"lastUpdateTs": current_timestamp, "key": "age", "value": user_attributes.get("age", "오류")},
        {"lastUpdateTs": current_timestamp, "key": "emotion", "value": user_attributes.get("emotion", "오류")},
        {"lastUpdateTs": current_timestamp, "key": "race", "value": user_attributes.get("race", "오류")}
    ]

    return jsonify(attributes), 200


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
