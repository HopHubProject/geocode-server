import os
import uvicorn
import pgeocode
import json
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = os.getenv("ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Geocode Server is running."}

@app.get("/geocode")
async def geocode(request: Request):
    zip = request.query_params.get("zip")
    nominatim = request.query_params.get("nominatim")

    if not zip or not nominatim:
        return Response(content="Missing 'zip' or 'nominatim' query parameters.", status_code=400)

    results = []

    for nom in nominatim.split(","):
        try:
            nomi = pgeocode.Nominatim(nom)
        except ValueError as e:
            continue

        pc = nomi.query_postal_code(zip)

        if not isinstance(pc.place_name, str):
            continue

        results.append({
            "postal_code": zip,
            "nominatim": nom,
            "latitude": pc.latitude,
            "longitude": pc.longitude,
            "place_name": pc.place_name
        })

    return Response(content=json.dumps(results), media_type="application/json")

@app.get("/health")
async def health():
    return Response(content="OK", media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, workers=4)