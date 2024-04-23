from .mc_native_type import MCNativeType
from .string import String
import json
import io


class Json(MCNativeType):
    @staticmethod
    def decode(stream: io.IOBase) -> dict:
        string = String.decode(stream)
        return json.loads(string)

    @staticmethod
    def encode(data: dict | list) -> bytearray:
        json_data = json.dumps(data)
        return String.encode(json_data)
