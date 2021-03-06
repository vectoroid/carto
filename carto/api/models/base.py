"""
Carto :: I/O Schema
- these schema are pydantic models (classes) which represent the application's
  I/O -- user input and app output, in the form of HTTPResponses, defined by 
  classes in FastAPI, or--more probably--Starlette.
"""
import contextlib
import logging

from fastapi.encoders import jsonable_encoder
from uuid import UUID, uuid4
from aiohttp import ClientError
from typing import Any, Callable, ClassVar, Dict, List, Tuple, Union
from pydantic import Extra
from pydantic import Field
from pydantic import BaseModel
from pydantic import ValidationError

from carto.api.config import AppSettings
from carto.api.exceptions import NotFoundHTTPException

# init logging
logger = logging.getLogger(__name__)

# init Deta SDK client
from deta import Deta
deta = Deta()

settings = AppSettings()


@contextlib.asynccontextmanager
async def async_db_client(db_name: str=settings.db_name):
    db_client = deta.AsyncBase(db_name)
    
    try:
        yield db_client
    except ClientError as e:
        print(e)
    finally:
        await db_client.close()
        

# Root subclass 
# -  simplest method to apply universal config options to all models
class DetaBase(BaseModel):
    """
    class: carto.api.models.DetaBase
    module: carto.api.models
    
    note: Didn't realize I'd have a reason to create an intermediary class, between pydantic.BaseModel and
          my actual I/O models, so by renaming (effectively) pydantic.BaseModel to pydantic.PydanticBase, 
          I avoid having to replace all instances of 'BaseModel' throughout the app.
          
    note: this is "heavily inspired by" (i.e. virtually plagiaristic in nature) the Monochrome API for Deta:
          
    """
    # key: str = None
    key: Union[UUID, str] = Field(default_factory=uuid4)
    db_name: ClassVar = Field(settings.db_name)
    
    class Config:
        """class carto.api.models.base.DetaBase.Config
        """
        anystr_strip_whitespace: bool = True    # always strip whitespace from user-input strings
        extra: str = Extra.forbid
        # extra: str = Extra.allow

    
    async def save(self):
        # increment version
        self.properties.version += 1 
        
        # save to Deta Base
        async with async_db_client(self.__class__.db_name) as db:
            new_feature = jsonable_encoder(self.dict())
            # Send to Deta to be saved:
            # -  DO NOT FORGET `await` statement! 
            # -  Upon success: Deta will return the saved item, if `db.put()` op was successful (else, no return value -- void)
            result = await db.put(new_feature) # note: using db.put() instead of db.insert(), b/c per Deta, db.put() is the faster method

        return result

            
    async def update(self, *args, **kwargs):
        """
        DetaBase.update [instance method]
        
        -  (1) increment version number
        -  (2) create a new dict from the keyword args passed to me
        -  (3) update my own dict, rather than create a new instance just yet
        -  (4) send my data as JSON to Deta Base(), to save it.
        -  (5) return a new instance of myself, instantiated with data returned from Deta (hah)
        """
        async with async_db_client(self.__class__.db_name) as db:
            new_data = {**self.dict(), **kwargs, "version": self.properties.version + 1}
            self.__dict__.update(**new_data)
            
            saved_data = await db.put(self.json()) # Deta.Base.put() should return new record
            
            # return new instance, instantiated with the saved data returned from Deta.Base():
            return self.__class__(**saved_data)

            
            
    async def delete(self) -> None:
        """
        DetaBase.delete() instance method
        -  returns simple text, "OK",  because deta.Deta.Base and deta.Deta.AsyncBase 
           always return None from their respective delete() methods.
        """
        async with async_db_client(self.__class__.db_name) as db:
            await db.delete(str(self.key))
        
        return "OK"
            
    @classmethod
    async def find(cls, key: Union[UUID, str], exception=NotFoundHTTPException) -> Union["DetaBase", None]:
        async with async_db_client(cls.db_name) as db:
            instance = await db.get(str(key))
            if instance is None and exception:
                raise exception(f"No Feature() found with key: {key}")
            elif instance:
                return cls(**instance)
            else:
                return None
            
    @classmethod
    async def fetch(cls, query=None, limit:int=50) -> List["DetaBase"]:
        """Feature.fetch() class method
        
        params:
            cls: the class reference
            query: an optional query to filter results
            limit: (optional) max number of items to retrieve for a single request.

        Returns:
            list[Feature]: returns a list of all items in the data store
            
        @NOTE:  limit param -- the default value is set to 50, only so I can verify that 
                               my settings in config.py are being read properly and applied.
                               As you'll see, however, this is superfluous and unnecessary, 
                               because when the 'limit' param is actually used, the MINIMUM 
                               of the user's 'limit' argument and the limit configured in 
                               settings.db_fetch_limit will be the value ultimately used when 
                               sending this request to DetaBase.
        
        @TODO:  (1) add pagination capability
        """
        async with async_db_client(cls.db_name) as db:
            if query is not None:
                query = jsonable_encoder(query)
                
            results = await db.fetch(query, limit=min(limit, settings.db_fetch_limit))
            all_items = results.items
            
            while len(all_items) <= limit and results.last:
                results = await db.fetch(query, last=results.last)
                all_items += results.items
                
            return [cls(**instance) for instance in all_items]
        
    @classmethod
    async def paginate(cls, query, limit:int, offset:int, order_by:Callable[["DetaBase"], str], do_reverse:bool=False) -> Tuple[int, List[Dict[str, Any]]]:
        if query is None:
            query = {}
            
        results = await cls.fetch(query, limit + offset)
        count = len(results)
        top = limit + offset
        page = sorted(results, key=order_by, reverse=do_reverse)[offset:top]
        
        return (count, page)
    
    @staticmethod
    async def delete_many(instances: List["DetaBase"]) -> str:
        for instance in instances:
            await instance.delete()
            
        return "OK"