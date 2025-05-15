from pydantic import BaseModel

class CategoryResponse(BaseModel):
    category_id: int
    category_major_name: str
    category_sub_name: str

    class Config:
        orm_mode = True