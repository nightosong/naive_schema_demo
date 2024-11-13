import os
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from modules.loaders import NacosJsonSchemaLoader as loader

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class ConfigData(BaseModel):
    schema_title: str
    schema_version: str
    description: str
    type: str
    properties: list


@app.get("/load_config", response_class=JSONResponse)
def load_config():
    try:
        return loader().download_from_nacos()
    except Exception:
        return JSONResponse(
            content={"error": "Configuration file not found"}, status_code=404
        )


@app.post("/save_config", response_class=JSONResponse)
def save_config(config_data: ConfigData):
    try:
        loader().upload_to_nacos(config_data.model_dump())
        return {"message": "Configuration saved successfully"}
    except Exception:
        return {"message": "Configuration save failed"}


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())


def set_system_environment(server_args) -> None:
    os.environ["env"] = server_args.env
    os.environ["nacos_addr"] = server_args.nacos_addr
    os.environ["nacos_group"] = server_args.nacos_group
    os.environ["nacos_data_id"] = server_args.nacos_data_id
    os.environ["nacos_user"] = server_args.nacos_user
    os.environ["nacos_password"] = server_args.nacos_password


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, required=False, help="environment name.")
    parser.add_argument("--address", type=str, required=True, help="server address")
    parser.add_argument("--port", type=str, default="8000", help="server port")
    parser.add_argument("--nacos_addr", type=str, required=True, help="nacos host")
    parser.add_argument(
        "--nacos_group", type=str, default="DEFAULT_GROUP", help="nacos group"
    )
    parser.add_argument("--nacos_data_id", type=str, required=True, help="data id.")
    parser.add_argument("--nacos_user", type=str, default="nacos", help="nacos user")
    parser.add_argument(
        "--nacos_password", type=str, default="nacos", help="nacos password"
    )
    args = parser.parse_args()
    set_system_environment(args)
    uvicorn.run(app, host=args.address, port=int(args.port))
