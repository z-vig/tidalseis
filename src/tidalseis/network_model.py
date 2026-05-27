from pydantic import BaseModel, computed_field
from datetime import datetime


class DeploymentTime(BaseModel):
    start: datetime
    end: datetime

    @computed_field
    def elapsed(self) -> str:
        return str(self.end - self.start)


class NetworkModel(BaseModel):
    code: str
    channels_of_interest: list[str]
    deployment_time: DeploymentTime
