# FastAPI delivery layer for LaunchLens.


# I use this file to connect the analysis to the outside world. It exposes the
# results through a small API and serves the dashboard, so the same analysis can
# be reviewed in the browser or used by another application.


from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .analysis import analyze_experiment
from .simulation import simulate_experiment

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
app = FastAPI(title="LaunchLens API", version="0.1.0", description="Evidence for confident AI product launches")


@lru_cache(maxsize=32)
def _analysis(seed: int, users: int):
    return analyze_experiment(simulate_experiment(users, seed))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/analysis")
def analysis(
    seed: int = Query(42, ge=0, le=1_000_000), users: int = Query(12_000, ge=200, le=100_000)
):
    return _analysis(seed, users)


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/static", StaticFiles(directory=WEB), name="static")


def run() -> None:
    import uvicorn

    uvicorn.run("launch_lens.api:app", host="127.0.0.1", port=8000, reload=False)

