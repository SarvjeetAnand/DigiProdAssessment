from pydantic import BaseModel, Field

class Product(BaseModel):
    id : int
    name : str
    price : float = Field(default=-1)
    stock : int = Field(default=-1)

    class Config:
        orm_mode = True
