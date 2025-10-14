from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, desc, asc, and_


class BaseRepository[EntityType]:
    def __init__(self, session: AsyncSession, entity: EntityType):
        self.session = session
        self.entity = entity

    async def bulk_create(self, entities: list[EntityType]) -> None:
        """
        Create multiple entities in the database without committing.
        """
        self.session.add_all(entities)
        await self.session.flush()

    async def create(self, entity: EntityType) -> None:
        """
        Create a new entity in the database without committing.
        """
        self.session.add(entity)
        await self.session.flush()

    async def get_one(
            self,
            id: Optional[UUID] = None,
            where: Optional[list] = None,
            options: Optional[list] = None,
    ) -> Optional[EntityType]:
        """
        Retrieve a single entity by specific filters. By default, searches by ID if provided.
        """
        stmt = select(self.entity)

        # Используем options, если они переданы
        if options:
            stmt = stmt.options(*options)

        # Если entity_id указан, ищем по ID
        if id is not None:
            stmt = stmt.where(self.entity.id == id)
        elif where:
            stmt = stmt.where(and_(*where))  # Если entity_id не указан, использует условия из where

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
            self,
            where: Optional[list] = None,
    ) -> list[EntityType]:
        """
        Retrieve all entities of the specified type.
        """
        query = select(self.entity)

        if where:
            query = query.where(and_(*where))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, id: UUID, data: dict) -> None:
        """
        Update an entity by its ID without committing.
        """
        query = (
            update(self.entity)
            .where(self.entity.id == id)
            .values(data)
        )
        await self.session.execute(query)

    async def update_partially(self, id: UUID, data: dict) -> None:
        """
        Update an entity by its ID with partial data without committing.
        """
        valid_fields = {column.name for column in self.entity.__table__.columns}  # Получаем набор валидных полей

        # Создаем словарь изменений, фильтруя по валидным полям и ненулевым значениям
        values = {field: value for field, value in data.items() if field in valid_fields and value is not None}

        if values:  # Проверяем, есть ли вообще изменения для обновления
            query = (
                update(self.entity)
                .where(self.entity.id == id)
                .values(values)
            )
            await self.session.execute(query)


    async def delete(self, id: UUID) -> None:
        """
        Delete an entity by its ID without committing.
        """
        query = delete(self.entity).where(self.entity.id == id)
        await self.session.execute(query)

    async def bulk_delete(self, ids: list[UUID], returning: Optional[list] = None) -> list | None:
        """
        Delete multiple entities by their IDs without committing.
        """
        query = delete(self.entity).where(self.entity.id.in_(ids))
        if returning:
            query = query.returning(*returning)

        result = await self.session.execute(query)
        if returning:
            return result.scalars().all()


    async def get_all_and_count(
            self,
            page: int,
            size: int,
            where: Optional[list] = None,
            options: Optional[list] = None,
            order_by: Optional[list[str]] = None,
    ) -> tuple[list[EntityType], int]:
        """
        Retrieve all entities of the specified type with optional filters.
        """
        stmt = select(self.entity)

        if options:
            stmt = stmt.options(*options)

        if where:
            stmt = stmt.where(and_(*where))

        count_stmt = stmt.with_only_columns(func.count(self.entity.id))

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar() or 0  # ✅ Если total = None, заменяем на 0

        # Apply ordering
        if order_by:
            for order in order_by:
                if order.startswith('-'):
                    # Descending order
                    column_name = order[1:]  # Remove the '-'
                    stmt = stmt.order_by(desc(getattr(self.entity, column_name)))
                else:
                    # Ascending order
                    stmt = stmt.order_by(asc(getattr(self.entity, order)))

        # Применяем пагинацию
        offset = page - 1 if page == 1 else (page - 1) * size
        paginated_query = stmt.limit(size).offset(offset)

        # Выполняем запрос
        result = await self.session.execute(paginated_query)
        items = result.scalars().all()

        return items, total