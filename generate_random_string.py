import random
import string


def generate_random_string(length=16):
    """ 지정된 길이의 랜덤 문자열 생성 (영문+숫자) """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))