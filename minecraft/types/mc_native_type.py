import io


class MCNativeType:  # only used for typing
    @staticmethod
    def decode(stream: io.IOBase):
        pass

    @staticmethod
    def encode(data) -> bytearray:
        pass
