DT_STORAGE = {}


class InMemoryTemplateStorage:
    def save(self, template_id: int, file_bytes: bytes) -> None:
        DT_STORAGE[template_id] = file_bytes

    def load(self, template_id: int) -> bytes:
        file_bytes = DT_STORAGE.get(template_id)
        if file_bytes is None:
            raise FileNotFoundError()

        return file_bytes

    def delete(self, template_id: int) -> None:
        if template_id in DT_STORAGE:
            del DT_STORAGE[template_id]
        else:
            raise FileNotFoundError()
