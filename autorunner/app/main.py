from fastapi import FastAPI

from autorunner import __version__
from .routers import deps, debugtalk, debug

app = FastAPI()


@app.get("/arun/version")
async def get_arun_version():
    return {"code": 0, "message": "success", "result": {"AutoRunner": __version__}}


app.include_router(deps.router)
app.include_router(debugtalk.router)
app.include_router(debug.router)
