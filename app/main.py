from fastapi import FastAPI

app = FastAPI(
    version="1.0",
    description="Internship project"
)

@app.get("/")
def main():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)