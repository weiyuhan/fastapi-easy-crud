from typing import (Annotated, Any, Generic, List, Optional, Type, TypeVar,
                    Union)

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

import fastapi_easy_crud.db.db_deps as deps
from fastapi_easy_crud.crud.crud_base import CRUDBase

CrudInstanceType = TypeVar("CrudInstanceType", bound=CRUDBase)

GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseAPI(
    Generic[CrudInstanceType, GetSchemaType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(
        self,
        prefix: str,
        tags: List[str],
        crud_instance: CrudInstanceType,
        get_schema_type: Type[GetSchemaType],
        create_schema_type: Type[CreateSchemaType],
        update_schema_type: Type[UpdateSchemaType],
    ) -> None:
        self.prefix = prefix
        self.tags = tags
        self.crud_instance = crud_instance
        self.get_schema_type = get_schema_type
        self.create_schema_type = create_schema_type
        self.update_schema_type = update_schema_type

    def to_model(self, db_model: Any) -> Optional[GetSchemaType]:
        return self.get_schema_type.model_validate(db_model) if db_model else None

    def to_models(self, db_models: List[Any]) -> List[Optional[GetSchemaType]]:
        return [self.to_model(m) for m in db_models]

    def init_router(self, router: APIRouter) -> None:
        crud_instance = self.crud_instance
        get_schema_type: Type[GetSchemaType] = self.get_schema_type
        create_schema_type: Type[CreateSchemaType] = self.create_schema_type
        update_schema_type: Type[UpdateSchemaType] = self.update_schema_type

        @router.get("/all", response_model=List[get_schema_type])  # type: ignore
        async def get_all(db: Session = Depends(deps.get_db)) -> Any:
            db_rows = crud_instance.get_multi(db=db)
            return self.to_models(db_rows)

        @router.get("/batch_get", response_model=List[get_schema_type])  # type: ignore
        async def get_by_ids(
            ids: Annotated[Union[List[Any], None], Query()] = None,
            db: Session = Depends(deps.get_db),
        ) -> Any:
            db_rows = crud_instance.batch_get(ids=ids, db=db)  # type: ignore
            return self.to_models(db_rows)

        @router.get("/get", response_model=Optional[get_schema_type])  # type: ignore
        async def get_by_id(id: str, db: Session = Depends(deps.get_db)) -> Any:
            db_row = crud_instance.get(id=id, db=db)
            return self.to_model(db_row)

        @router.post("/create", response_model=Optional[get_schema_type])  # type: ignore
        async def create(
            create_obj: create_schema_type, db: Session = Depends(deps.get_db)  # type: ignore
        ) -> Any:
            db_row = crud_instance.create(db=db, obj_in=create_obj)
            return self.to_model(db_row)

        @router.post("/batch_create", response_model=List[get_schema_type])  # type: ignore
        async def batch_create(
            create_objs: List[create_schema_type], db: Session = Depends(deps.get_db)  # type: ignore
        ) -> Any:
            db_rows = crud_instance.batch_create(db=db, objs=create_objs)
            return self.to_models(db_rows)

        @router.post("/batch_create_silently")  # type: ignore
        async def batch_create_silently(
            create_objs: List[create_schema_type], db: Session = Depends(deps.get_db)  # type: ignore
        ) -> Any:
            crud_instance.batch_create_silently(db=db, objs=create_objs)
            return "success"

        @router.put("/update", response_model=Optional[get_schema_type])  # type: ignore
        async def update(
            origin_obj: get_schema_type,  # type: ignore
            update_obj: update_schema_type,  # type: ignore
            db: Session = Depends(deps.get_db),
        ) -> Any:
            db_row = crud_instance.update(db=db, db_obj=origin_obj, obj_in=update_obj)
            return self.to_model(db_row)

        @router.put("/update_by_id", response_model=Optional[get_schema_type])
        async def update_by_id(
            id: str,
            update_obj: update_schema_type,  # type: ignore
            db: Session = Depends(deps.get_db),
        ) -> Any:
            db_row = crud_instance.update_by_id(db=db, id=id, obj_in=update_obj)
            return self.to_model(db_row)

        @router.delete("/delete", response_model=Optional[get_schema_type])
        async def delete(id: str, db: Session = Depends(deps.get_db)) -> Any:
            db_row = crud_instance.remove(db=db, id=id)
            return self.to_model(db_row)

    def enhance_router(self, router: APIRouter) -> None:
        pass
