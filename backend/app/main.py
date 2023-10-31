from app.app import app
from app.routes.auth import router as AuthRouter
from app.routes.generate import router as GenerateRouter
from app.routes.users import router as UserRouter
from app.routes.translate import router as TranslateRouter
from app.routes.transcribe import router as TranscribeRouter
from app.routes.completion import router as CompletionRouter
from app.routes.model import router as ModelRouter
from app.routes.suggestion import router as SuggestionRouter
from app.routes.chat import router as ChatRouter
from app.routes.payment import router as PaymentRouter
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AuthRouter)
app.include_router(GenerateRouter)
app.include_router(UserRouter)
app.include_router(TranslateRouter)
app.include_router(TranscribeRouter)
app.include_router(CompletionRouter)
app.include_router(ModelRouter)
app.include_router(SuggestionRouter)
app.include_router(ChatRouter)
app.include_router(PaymentRouter)
