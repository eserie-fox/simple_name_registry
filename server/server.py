from fastapi import FastAPI, HTTPException
import json
import os
from datetime import datetime
import uvicorn


app = FastAPI()


def load_records(record_file_path: str):
    if os.path.exists(record_file_path):
        with open(record_file_path, "r") as f:
            return json.load(f)
    return {}


def save_records(records, record_file_path: str):
    with open(record_file_path, "w") as f:
        json.dump(records, f, indent=4)


def get_config():
    with open("./config.json", "r") as f:
        config = json.load(f)
        if "record_file" not in config:
            raise ValueError("Missing 'record_file' in config.json")
        if "read_password" not in config:
            raise ValueError("Missing 'read_password' in config.json")
        if "put_password" not in config:
            raise ValueError("Missing 'put_password' in config.json")
        return config


@app.put("/record")
async def put_record(name: str, ip_address: str, mac_address: str, put_password: str):
    config = get_config()
    if put_password != config["put_password"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    records = load_records(config["record_file"])
    records[name] = {
        "ip_address": ip_address,
        "mac_address": mac_address,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_records(records, config["record_file"])
    return {"message": "Record added successfully"}


@app.get("/records")
async def get_records(read_password: str):
    config = get_config()
    if read_password != config["read_password"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    records = load_records(config["record_file"])
    return records


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=get_config()["listen_port"])
