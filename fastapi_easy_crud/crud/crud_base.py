from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.orm import Session

from fastapi_easy_crud.db.db_base import CommonBase as Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """  # noqa
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()  # type: ignore

    def batch_get(self, db: Session, *, ids: List[Any]) -> List[ModelType]:
        return db.query(self.model).filter(self.model.id.in_(ids)).all()  # type: ignore

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def batch_create(
        self, db: Session, *, objs: List[CreateSchemaType]
    ) -> List[ModelType]:
        data_inputs = [jsonable_encoder(obj_in, exclude_unset=True) for obj_in in objs]
        models = [self.model(**data_input) for data_input in data_inputs]
        db.add_all(models)
        db.commit()
        db.expire_all()
        return models

    def batch_create_silently(
        self, db: Session, *, objs: List[CreateSchemaType]
    ) -> None:
        data_inputs = [jsonable_encoder(obj_in, exclude_unset=True) for obj_in in objs]
        stmt = insert(self.model).values(data_inputs)  # type: ignore
        db.execute(stmt)
        db.commit()

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_by_id(
        self, db: Session, *, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        db_obj = self.get(db, id=id)
        if db_obj is not None:
            return self.update(db, db_obj=db_obj, obj_in=obj_in)
        else:
            logger.error(
                f"update_by_id: {id} not found in tbale {self.model.__tablename__}"
            )
            return None

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if obj is None:
            return None
        db.delete(obj)
        db.commit()
        return obj
