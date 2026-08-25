from pydantic import BaseModel, Field

class PredictionInput(BaseModel):
    # Field(...) means required. Constraints: gt (greater than), ge (greater/equal), le (less/equal)
    MedInc: float = Field(..., gt=0, description="Median Income in block group (in $10,000s). Must be > 0")
    HouseAge: float = Field(..., ge=0, le=100, description="Median House Age in block group (0 to 100 years)")
    AveRooms: float = Field(..., gt=0, description="Average number of rooms per household")
    AveBedrms: float = Field(..., gt=0, description="Average number of bedrooms per household")
    Population: float = Field(..., ge=0, description="Block group population")
    AveOccup: float = Field(..., gt=0, description="Average household occupancy rate")
    
    # Custom constraints on geographical coordinates:
    Latitude: float = Field(..., ge=32.0, le=42.0, description="California Latitude coordinate (32.0 to 42.0)")
    Longitude: float = Field(..., ge=-125.0, le=-114.0, description="California Longitude coordinate (-125.0 to -114.0)")

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