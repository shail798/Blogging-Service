from fastapi import FastAPI
from app.api import blog_routes

app = FastAPI()

# Register the blog routes
app.include_router(blog_routes.router)
