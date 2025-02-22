from deepface import DeepFace


def analyze_face(image_path):
    """ DeepFace를 사용하여 나이, 성별, 감정을 분석하는 함수 """
    try:
        # DeepFace 분석 실행
        result = DeepFace.analyze(img_path=image_path, actions=["age", "gender", "emotion", "race"])#, enforce_detection=False

        if not result or isinstance(result, list) and len(result) == 0:
            return {"error": "No face detected"}

        # 분석 결과 추출
        age = result[0]["age"]
        korean_age = age + 1  # 한국 나이 변환
        gender = result[0]["dominant_gender"]
        emotion = result[0]["dominant_emotion"]
        race = result[0]["dominant_race"]

        # 성별을 한글로 변환
        gender_korean = "남성" if gender in ["Man", "male"] else "여성"

        # 감정을 한글로 변환
        emotion_dict = {
            "angry": "화남", "disgust": "혐오", "fear": "두려움",
            "happy": "행복", "sad": "슬픔", "surprise": "놀람", "neutral": "중립"
        }
        emotion_korean = emotion_dict.get(emotion, "알 수 없음")

        # 인종을 한글로 변환
        race_dict = {
            "asian": "아시아인",
            "white": "백인",
            "middle eastern": "중동계",
            "latino hispanic": "라틴계/히스패닉",
            "black": "흑인"
        }
        race_korean = race_dict.get(race, "알 수 없음")

        # 분석 결과 딕셔너리 반환
        return {
            "age": str(korean_age),
            "gender": gender_korean,
            "emotion": emotion_korean,
            "race": race_korean
        }

    except Exception as e:
        print(f"DeepFace 분석 오류: {e}")
        return None  # 오류 발생 시 None 반환
