"""AI Classroom package — Voice Chat + Peer Teaching engines."""
from .voice_chat_engine   import VoiceChatEngine
from .peer_teaching_engine import PeerTeachingEngine
from .classroom_manager   import ClassroomManager

voice_engine    = VoiceChatEngine()
peer_engine     = PeerTeachingEngine()
classroom_mgr   = ClassroomManager()

__all__ = ["voice_engine", "peer_engine", "classroom_mgr",
           "VoiceChatEngine", "PeerTeachingEngine", "ClassroomManager"]
