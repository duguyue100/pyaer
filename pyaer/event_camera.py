class EventCamera:
    def __init__(self) -> None:
        self.camera = None

    def __enter__(self) -> None:
        return self.camera

    # context manager exist method with typing
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.camera.shutdown()
