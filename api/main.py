from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
import json
from my_db import *
from pydantic import BaseModel


class IMEIRequest(BaseModel):
    imei: str
    token: str


app = FastAPI()


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


@app.post("/api/check-imei")
async def check_imei(request: IMEIRequest):
    imei = request.imei
    if not validate(imei):
        return JSONResponse(content={"error": "Неверный IMEI"}, status_code=400)

    existing_check = await find_check(imei)
    if existing_check is not None:
        return JSONResponse(content=existing_check, status_code=200)

    url = "https://api.imeicheck.net/v1/checks"
    payload = json.dumps({
        "deviceId": imei,
        "serviceId": 15
    })
    headers = {
        'Authorization': f'Bearer {request.token}',
        'Content-Type': 'application/json'
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, data=payload)

                if response.status_code == 201:
                    response_data = response.json()
                    if response_data["status"] == "successful":
                        await add_check(imei=imei, check_status=True, check_details=response_data)
                        return JSONResponse(content=response_data, status_code=201)

                    elif response_data["status"] == "unsuccessful":
                        response_data["properties"] = {
                            "Информация": " не найдена"}
                        await add_check(imei=imei, check_status=True, check_details=response_data)
                        return JSONResponse(content=response_data, status_code=201)
                    else:
                        continue
                else:
                    error_details = {
                        "error": "api",
                        "status_code": response.status_code,
                        "response": response.json() if response.text else {}
                    }
                    if response.status_code >= 429:
                        continue
                    return JSONResponse(content=error_details, status_code=response.status_code)

        except Exception as e:
            if attempt == max_retries - 1:
                return JSONResponse(content={"error": "Максимальное количество попыток использовано", "details": str(e)}, status_code=503)

    return JSONResponse(content={"error": "Сервис временно недоступен. Повторите попытку позже."}, status_code=503)
