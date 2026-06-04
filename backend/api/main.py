from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import upload, query, sessions
from core.config import PORT

app = FastAPI(
    title='ContractIQ API',
    description='Agentic Legal Contract Intelligence Platform',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(upload.router)
app.include_router(query.router)
app.include_router(sessions.router)


@app.get('/api/health')
async def health_check():
    return {'status': 'healthy', 'service': 'ContractIQ API'}


@app.get('/')
async def root():
    return {'message': 'ContractIQ API', 'version': '1.0.0', 'docs': '/docs'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=PORT)
