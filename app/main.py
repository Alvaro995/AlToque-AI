from fastapi import FastAPI

app = FastAPI(
    title="AlToque AI API",
    description="Backend central de AlToque AI",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "application": "AlToque AI",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "service": "altoque-ai",
        "status": "ok"
    }