import yaml
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from libs.tools import run_code_with_error
from libs.speech_recognition import load_whisper, transcribe
from libs.text_generation import (
    load_hf_hosted_model,
    load_ollama_model,
    run_prompt,
)

from rivet_graph_utils import build_project

app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

## Updating Auth tokens
with open('auth.yaml', 'r') as f:

    auth={
        "graph_description": "auth tokens",
        "graph_id": "7NcPhV8OHI8jI3uzYn4fK",
        "graph_name": "presets/auth_presets",
        "values":yaml.safe_load(f),
        "values_type": "string"
    }

with open(f"./models/presets/auth_presets.yaml", "w") as f:
    yaml.dump(auth, f)


## Choosing what presets use in the project
presets=[
    'auth_presets',
    'hf_open_llm_presets',
    'stop_sequences_presets',
    'temperature_presets',
    'ollama_llm_presets',
    'context_len_presets',
]

# get_methods = {
#     'get_ollama'
# }

methods = {
    "load_hf_hosted_model": load_hf_hosted_model,
    'load_ollama_model':load_ollama_model,
    "load_whisper":load_whisper,
    "run_prompt": run_prompt,
    "transcribe": transcribe,
    "run_code_with_error":run_code_with_error,
}

## Not implemented yet
flows = {}


# Add Methods
for method in methods:
    router.add_api_route(f"/methods/{method}", methods[method], methods=["POST"])

# Add the routes
app.include_router(router)


if __name__ == "__main__":
    graph_ids, graph = build_project(
        "VisualFlows",
        presets,
        methods,
        flows,
        api_base="http://localhost:8000",
        height=3000,
        width=16000,
        padding=200,
        secondary_padding=50,
    )
