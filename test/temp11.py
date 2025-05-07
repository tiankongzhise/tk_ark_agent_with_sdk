from pydantic import BaseModel

class testClass(BaseModel):
    x:str
    
test_dict = {'x':'1','y':2}

test_obj = testClass(**test_dict)

print(test_obj)
