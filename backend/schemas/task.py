from pydantic import BaseModel

class CreateTaskRequest(BaseModel):
    clientKey: str
    task: dict

class GetTaskRequest(BaseModel):
    clientKey: str
    taskId: str
