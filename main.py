from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from io import BytesIO
import uuid
from utils.img import generate_mock_image



# Define the schema for the bounding box
class BoundingBox(BaseModel):
    x_min: int  # Minimum x-coordinate of the bounding box
    y_min: int  # Minimum y-coordinate of the bounding box
    x_max: int  # Maximum x-coordinate of the bounding box
    y_max: int  # Maximum y-coordinate of the bounding box
    color: str  # Color of the bounding box (e.g., 'red', 'blue')
    shape: str  # Shape associated with the bounding box (e.g., 'rectangle', 'ellipse')


# Define the schema for the request body
class BoundingBoxRequest(BaseModel):
    image_id: str  # Unique identifier of the image
    bboxes: List[BoundingBox]  # List of bounding boxes for the image


# Initialize the FastAPI app
app = FastAPI(
    title="Image Annotation API",
    description="""
    This API allows users to:
    - Generate mock images and retrieve them via a unique ID.
    - Submit bounding boxes for an image, ensuring validation and storage.
    """,
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with specific domains for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Image-ID"],
)

@app.get(
    "/get-mock-image",
    summary="Generate and stream a mock image",
    description="""
    This endpoint generates a mock image, streams it as a PNG, and returns a unique `image_id`
    in the response headers. The `image_id` can be used for associating annotations.
    """,
    responses={
        200: {
            "content": {"image/png": {}},
            "headers": {
                "Image-ID": {
                    "description": "Unique identifier for the generated image",
                    "schema": {"type": "string"},
                }
            },
        }
    },
)
async def generate_image():
    """
    Generate a mock image and stream it as a PNG with a unique ID.
    """
    # Generate a unique image ID
    image_id = str(uuid.uuid4())

    # Generate the mock image
    image = generate_mock_image()

    # Create a generator to stream image data
    def image_stream():
        with BytesIO() as buffer:
            image.save(buffer, format="PNG")
            buffer.seek(0)
            yield buffer.read()

    # Prepare response with the image ID
    headers = {"Image-ID": image_id}
    return StreamingResponse(image_stream(), media_type="image/png", headers=headers)


@app.post(
    "/submit-bbox",
    summary="Submit bounding boxes for an image",
    description="""
    This endpoint accepts a list of bounding boxes for an image identified by `image_id`.
    The bounding boxes are validated to ensure they have valid coordinates.
    """,
    responses={
        200: {
            "description": "Bounding boxes received successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Bounding boxes received successfully",
                        "image_id": "123e4567-e89b-12d3-a456-426614174000",
                        "bboxes": [
                            {
                                "x_min": 10,
                                "y_min": 20,
                                "x_max": 100,
                                "y_max": 200,
                                "color": "red",
                                "shape": "rectangle",
                            }
                        ],
                    }
                }
            },
        },
        400: {
            "description": "Invalid bounding box coordinates.",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid bounding box coordinates."}
                }
            },
        },
    },
)
async def submit_bboxes(data: BoundingBoxRequest):
    """
    Validate and process bounding boxes submitted for an image.
    """
    for bbox in data.bboxes:
        if bbox.x_min >= bbox.x_max or bbox.y_min >= bbox.y_max:
            raise HTTPException(
                status_code=400, detail="Invalid bounding box coordinates."
            )

    # Log received data (for development purposes)
    print("image_id", data.image_id)
    print("bboxes", data.bboxes)

    return {
        "message": "Bounding boxes received successfully",
        "image_id": data.image_id,
        "bboxes": data.bboxes,
    }


@app.get("/")
async def read_root():
    return {"message": "Hello, World!!!"}
