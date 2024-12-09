from server import PromptServer
from aiohttp import web
import folder_paths
import os
import logging

import struct
import json
import pathlib


@PromptServer.instance.routes.get("/a8r8/loras")
async def loras(request):
    try:
        loras = [
            {
                "path": lora,
                "name": pathlib.Path(lora).stem,
                "metadata": get_lora_metadata(lora),
            }
            for lora in folder_paths.get_filename_list("loras")
        ]

        return web.json_response(loras)
    except Exception as e:
        logging.error(e)
        return web.Response(status=400, text=str(e))


@PromptServer.instance.routes.get("/a8r8/health")
async def health(_request):
    try:
        return web.json_response(
            {},
            status=200,
        )
    except Exception as e:
        logging.error(e)
        return web.Response(status=400, text=str(e))


def get_lora_metadata(lora):
    try:
        if ".safetensors" in lora:
            base_path = folder_paths.folder_names_and_paths["loras"][0][0]

            lora_path = os.path.join(base_path, lora)

            return read_metadata(lora_path)
        return None
    except FileNotFoundError as _e:
        return None


def read_metadata(file_path):
    # Open the file in binary mode
    with open(file_path, "rb") as io_device:
        # Read 8 bytes and unpack as little-endian unsigned integer
        n_bytes = io_device.read(8)

        n = struct.unpack("<Q", n_bytes)[
            0
        ]  # '<Q' means little-endian unsigned long long

        # Read n bytes and decode JSON
        metadata_bytes = io_device.read(n)
        io_device.close()
        metadata = json.loads(metadata_bytes.decode("utf-8"))

        # Retrieve the value associated with "__metadata__"
        return metadata.get("__metadata__")
