"""
DATA ENGINE — Frontal Lobe / Memory Core
Central controller for all memory/data behavior in ODEX.
Receives data from uploads, builds, user edits, chat, workspace, and routes to the appropriate memory modules.
"""

from data_engine.working_memory import WorkingMemory
from data_engine.long_term_memory import LongTermMemory
from data_engine.retrieval_engine import RetrievalEngine
from data_engine.context_linker import ContextLinker
from data_engine.preference_memory import PreferenceMemory
from data_engine.upload_memory import UploadMemory
from data_engine.memory_guard import MemoryGuard
from data_engine.sql_bridge import SQLBridge
from data_engine.vector_bridge import VectorBridge

class DataCore:
    def __init__(self):
        self.working_memory = WorkingMemory()
        self.long_term_memory = LongTermMemory()
        self.retrieval_engine = RetrievalEngine(self)
        self.context_linker = ContextLinker(self)
        self.preference_memory = PreferenceMemory()
        self.upload_memory = UploadMemory()
        self.memory_guard = MemoryGuard(self)
        self.sql_bridge = SQLBridge()
        self.vector_bridge = VectorBridge()

    def receive_data(self, data, source):
        """
        Entry point for all data coming into the Data Engine.
        Decides where to store and how to process it.
        """
        # Example: Route to working memory if active, else long-term, etc.
        pass

    def retrieve(self, query, context=None):
        """
        Retrieve memory/data based on query and context.
        """
        return self.retrieval_engine.retrieve(query, context)






