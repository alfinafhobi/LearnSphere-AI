from .auth_router import router as auth_router
from .subjects_router import router as subjects_router
from .assessment_router import router as assessment_router
from .planner_router import router as planner_router
from .tutor_router import router as tutor_router
from .quiz_router import router as quiz_router
from .analytics_router import router as analytics_router
from .agents_router import router as agents_router
from .profile_router import router as profile_router

__all__ = [
    "auth_router",
    "subjects_router",
    "assessment_router",
    "planner_router",
    "tutor_router",
    "quiz_router",
    "analytics_router",
    "agents_router",
    "profile_router"
]
