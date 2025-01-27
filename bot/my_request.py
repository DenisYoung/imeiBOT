from dotenv import load_dotenv
import httpx
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def validate(imei: str) -> bool:
    if not imei.isdigit() or len(imei) not in (14, 15):
        return False

    imei_digits = list(map(int, imei))
    checksum = 0

    for i in range(len(imei_digits)):
        digit = imei_digits[-1 - i]
        if i % 2 == 0:
            checksum += digit
        else:
            doubled = digit * 2
            checksum += doubled if doubled < 10 else doubled - 9

    return checksum % 10 == 0


async def get_info(imei: str):
    if not validate(imei):
        return {"error": "Ошибка валидации"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            
            response = await client.post("http://imei_api:8000/api/check-imei", json={"imei": imei, "token": SECRET_KEY})
            return response.json()

    except Exception as e:
        return {"error": "Ошибка запроса"}
