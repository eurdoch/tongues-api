from app.app import app
from app.routes.generate import router as GenerateRouter
from app.routes.users import router as UserRouter
from app.routes.translate import router as TranslateRouter
from app.routes.transcribe import router as TranscribeRouter
from app.routes.suggestion import router as SuggestionRouter
from app.routes.chat import router as ChatRouter
from app.routes.audio import router as AudioRouter
from app.routes.ping import router as PingRouter
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(PingRouter)
app.include_router(GenerateRouter)
app.include_router(UserRouter)
app.include_router(TranslateRouter)
app.include_router(TranscribeRouter)
app.include_router(SuggestionRouter)
app.include_router(ChatRouter)
app.include_router(AudioRouter)
