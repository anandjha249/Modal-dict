import os

import modal
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = modal.Dict.from_name("hls-poc")


@app.get("/{path:path}")
async def get_file(path: str):
    try:
        data = store[path]
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )

    if path.endswith(".m3u8"):
        mime = "application/vnd.apple.mpegurl"

    elif path.endswith(".ts"):
        mime = "video/mp2t"

    elif path.endswith(".vtt"):
        mime = "text/vtt"

    else:
        mime = "application/octet-stream"

    return Response(
        content=data,
        media_type=mime,
        headers={
            "Cache-Control": "public, max-age=60",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/")
async def root():
    return {
        "status": "ok",
        "dict": "hls-poc",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                8000,
            )
        ),
    )
