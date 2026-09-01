# app/models/schemas.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PredictionInput(BaseModel):
    MedInc: float = Field(..., gt=0, description="Median Income in block group (in $10,000s)")
    HouseAge: float = Field(..., ge=0, le=100, description="Median House Age in block group")
    AveRooms: float = Field(..., gt=0, description="Average number of rooms per household")
    AveBedrms: float = Field(..., gt=0, description="Average number of bedrooms per household")
    Population: float = Field(..., ge=0, description="Block group population")
    AveOccup: float = Field(..., gt=0, description="Average household occupancy rate")
    Latitude: float = Field(..., ge=32.0, le=42.0, description="California Latitude coordinate")
    Longitude: float = Field(..., ge=-125.0, le=-114.0, description="California Longitude coordinate")

    class Config:
        json_schema_extra = {
            "example": {
                "MedInc": 8.3252,
                "HouseAge": 41.0,
                "AveRooms": 6.9841,
                "AveBedrms": 1.0238,
                "Population": 322.0,
                "AveOccup": 2.5555,
                "Latitude": 37.88,
                "Longitude": -122.23
            }
        }

class PredictionOutput(BaseModel):
    request_id: str = Field(..., description="Unique UUID for request tracing")
    predicted_price_usd: str = Field(..., description="Formatted prediction price in USD")
    raw_prediction: float = Field(..., description="Raw output value from Scikit-Learn pipeline")
    confidence_score: Optional[float] = Field(None, description="Confidence score if applicable")
    model_version: str = Field("1.0.0", description="Version of the model serving inference")

# 11 BATCH & METADATA SCHEMAS
class PredictionBatchInput(BaseModel):
    inputs: List[PredictionInput] = Field(..., min_length=1, max_length=100, description="List of 1 to 100 housing samples")

class PredictionBatchOutput(BaseModel):
    request_id: str = Field(..., description="Unique batch request UUID")
    batch_size: int = Field(..., description="Number of items processed in this batch")
    predictions: List[PredictionOutput] = Field(..., description="List of individual prediction outputs")

class ModelInfoOutput(BaseModel):
    model_name: str = Field(..., description="Name of the machine learning model")
    model_type: str = Field(..., description="Class type of the Scikit-Learn pipeline")
    model_version: str = Field(..., description="Semantic version of the model artifact")
    features: List[str] = Field(..., description="List of expected input feature names in order")
    target: str = Field(..., description="Target variable name being predicted")
    trained_on: str = Field(..., description="Dataset name used for training")