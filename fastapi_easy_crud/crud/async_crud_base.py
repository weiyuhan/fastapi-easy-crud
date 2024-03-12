from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_easy_crud.db.db_base import CommonBase as Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AsyncCRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """  # noqa
        self.model = model

    async def get(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar()

    async def batch_get(self, db: AsyncSession, *, ids: List[Any]) -> List[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id.in_(ids)))
        return list(result.scalars().all())

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def batch_create(
        self, db: AsyncSession, *, objs: List[CreateSchemaType]
    ) -> List[ModelType]:
        data_inputs = [jsonable_encoder(obj_in, exclude_unset=True) for obj_in in objs]
        models = [self.model(**data_input) for data_input in data_inputs]
        db.add_all(models)
        await db.commit()
        db.expire_all()
        return models

    async def batch_create_silently(
        self, db: AsyncSession, *, objs: List[CreateSchemaType]
    ) -> None:
        data_inputs = [jsonable_encoder(obj_in, exclude_unset=True) for obj_in in objs]
        stmt = insert(self.model).values(data_inputs)
        await db.execute(stmt)
        await db.commit()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_by_id(
        self,
        db: AsyncSession,
        *,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        db_obj = await self.get(db, id=id)
        if db_obj is not None:
            return await self.update(db, db_obj=db_obj, obj_in=obj_in)
        else:
            logger.error(
                f"update_by_id: {id} not found in tbale {self.model.__tablename__}"
            )
            return None

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        obj = result.scalar()
        if obj:
            await db.delete(obj)
            await db.commit()
            return obj
        else:
            return None
