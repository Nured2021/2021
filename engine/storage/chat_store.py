class ChatStore:
    def __init__(self):
        self.chat_memory = []
    def store_prompt(self, prompt):
        self.chat_memory.append({"type": "prompt", "data": prompt})
    def store_file(self, file_data):
        self.chat_memory.append({"type": "file", "data": file_data})
    def store_edit(self, edit):
        self.chat_memory.append({"type": "edit", "data": edit})
    def get_memory(self):
        return self.chat_memory






