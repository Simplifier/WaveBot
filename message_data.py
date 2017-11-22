class MessageData:
    def __init__(self, id: int, timestamp: int, text: str):
        self.id = id
        self.timestamp = timestamp
        self.text = text
        self.doc_id: int = 0
        self.photo_id: int = 0
