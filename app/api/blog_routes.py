# blog_routes.py

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.blog_service import BlogService
from app.models.blog import Blog
from app.constants.response_constants import RESPONSE_MESSAGES
import logging

router = APIRouter()
blog_service = BlogService()

# Set up logging for visibility
logging.basicConfig(level=logging.INFO)

@router.post("/submit_blog/")
async def submit_blog(blog: Blog):
    try:
        blog_service.submit_blog(blog)
        logging.info("Blog submission processed successfully.")
        # Use JSONResponse for success with status code 201 (Created)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"status": RESPONSE_MESSAGES["BLOG_SUBMITTED"]}
        )
    except ValueError as e:
        logging.error(f"Validation error during blog submission: {e}")
        # Use HTTPException for validation error (4xx client-side error)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=RESPONSE_MESSAGES["VALIDATION_ERROR"]
        )
    except Exception as e:
        logging.error(f"Error during blog submission: {e}")
        # Use HTTPException for internal server error (5xx server-side error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=RESPONSE_MESSAGES["BLOG_SUBMISSION_FAILED"]
        )

@router.get("/search/")
async def search_blog(query: str):
    try:
        results = blog_service.search_blog(query)
        logging.info(f"Search processed successfully for query: {query}")
        # Use JSONResponse for success with status code 200 (OK)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=results
        )
    except ValueError as e:
        logging.error(f"Validation error during search: {e}")
        # Use HTTPException for validation error (4xx client-side error)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=RESPONSE_MESSAGES["VALIDATION_ERROR"]
        )
    except Exception as e:
        logging.error(f"Error during search: {e}")
        # Use HTTPException for internal server error (5xx server-side error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=RESPONSE_MESSAGES["SEARCH_FAILED"]
        )
