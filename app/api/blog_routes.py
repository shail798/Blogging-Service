from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.blog_service import BlogService
from app.models.blog import Blog
from app.constants.response_constants import RESPONSE_MESSAGES
import logging
from pydantic import ValidationError

router = APIRouter()
blog_service = BlogService()

logging.basicConfig(level=logging.INFO)

@router.post("/submit_blog/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_blog(blog: Blog):
    try:
        blog_service.submit_blog(blog)
        logging.info("Blog submission processed successfully.")
        return {"status": RESPONSE_MESSAGES["BLOG_SUBMITTED"]}
    except ValidationError as e:
        logging.error(f"Validation error during blog submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ValueError as e:
        logging.error(f"Value error during blog submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RESPONSE_MESSAGES["VALIDATION_ERROR"]
        )
    except ConnectionError as ce:
        logging.error(f"RabbitMQ connection error: {ce}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable. Please try again later."
        )
    except Exception as e:
        logging.error(f"Unexpected error during blog submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=RESPONSE_MESSAGES["BLOG_SUBMISSION_FAILED"]
        )

@router.get("/search/", response_model=list, status_code=status.HTTP_200_OK)
async def search_blog(user_id: str = None, text: str = None):
    try:
        results = await blog_service.search_blog(user_id=user_id, text=text)
        if not results:
            logging.info(f"No results found for user_id: {user_id}, text: {text}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": RESPONSE_MESSAGES["NO_RESULTS_FOUND"]}
            )
        logging.info(f"Search processed successfully for user_id: {user_id}, text: {text}")
        return results
    except ValidationError as e:
        logging.error(f"Validation error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ValueError as e:
        logging.error(f"Value error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RESPONSE_MESSAGES["VALIDATION_ERROR"]
        )
    except ConnectionError as ce:
        logging.error(f"Elasticsearch connection error: {ce}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable. Please try again later."
        )
    except Exception as e:
        logging.error(f"Unexpected error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=RESPONSE_MESSAGES["SEARCH_FAILED"]
        )
