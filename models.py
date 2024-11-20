from pydantic import BaseModel 

class AbsoluteBaseModel(BaseModel): 
    filename: str 
    email_id: str 
    
class ConvertPDFModel(AbsoluteBaseModel): 
    uri: str 

class ConvertPDFOutputModel(AbsoluteBaseModel): 
    uri: str 
    time: float # in seconds 