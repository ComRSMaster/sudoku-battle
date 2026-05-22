from pydantic import BaseModel


class AchievementSchema(BaseModel):
    sprinter: bool = False
    advanced_player: bool = False
    master: bool = False

    class Config:
        from_attributes = True
