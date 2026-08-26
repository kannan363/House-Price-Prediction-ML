from pydantic import BaseModel, Field

class PredictionInput(BaseModel):
    MedInc: float = Field(..., gt=0, description="Median Income in $10k units")
    HouseAge: float = Field(..., ge=0, le=100, description="Median House Age")
    AveRooms: float = Field(..., gt=0, description="Average Rooms per house")
    AveBedrms: float = Field(..., gt=0, description="Average Bedrooms per house")
    Population: float = Field(..., ge=0, description="Block Population")
    AveOccup: float = Field(..., gt=0, description="Average Household Occupancy")
    Latitude: float = Field(..., ge=32.0, le=42.0, description="California Latitude")
    Longitude: float = Field(..., ge=-125.0, le=-114.0, description="California Longitude")

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