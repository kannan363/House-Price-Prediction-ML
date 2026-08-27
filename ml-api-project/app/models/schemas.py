from typing import Optional
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

#8 RESPONSE SCHEMA ---
class PredictionOutput(BaseModel):
    request_id: str = Field(..., description="Unique UUID for request tracing")
    predicted_price_usd: str = Field(..., description="Formatted prediction price in USD")
    raw_prediction: float = Field(..., description="Raw output value from Scikit-Learn pipeline")
    confidence_score: Optional[float] = Field(None, description="Confidence score if applicable (null for regression)")
    model_version: str = Field("1.0.0", description="Version of the model serving inference")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "predicted_price_usd": "$415,194.02",
                "raw_prediction": 4.1519402,
                "confidence_score": None,
                "model_version": "1.0.0"
            }
        }