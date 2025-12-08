"""Base repository with generic CRUD operations."""

from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.schema import Base
from src.adhd_planner.utils.logger import get_logger

# Type variable for the SQLAlchemy model
ModelType = TypeVar("ModelType", bound=Base)

logger = get_logger("repository")


class BaseRepository(Generic[ModelType]):
    """Generic repository for database operations."""

    def __init__(self, model: Type[ModelType], session: Session):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session
        self.logger = logger

    def create(self, data: Dict[str, Any]) -> ModelType:
        """
        Create a new entity.

        Args:
            data: Dictionary of field values

        Returns:
            Created entity

        Raises:
            Exception: If creation fails
        """
        try:
            entity = self.model(**data)
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)

            self.logger.info(
                f"Created {self.model.__name__} with id: {entity.id}"
            )
            return entity

        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error creating {self.model.__name__}: {e}",
                exc_info=True
            )
            raise

    def get_by_id(self, entity_id: str) -> Optional[ModelType]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity or None if not found
        """
        try:
            entity = self.session.query(self.model).filter(
                self.model.id == entity_id
            ).first()

            if entity:
                self.logger.debug(
                    f"Found {self.model.__name__} with id: {entity_id}"
                )
            else:
                self.logger.debug(
                    f"{self.model.__name__} not found with id: {entity_id}"
                )

            return entity

        except Exception as e:
            self.logger.error(
                f"Error getting {self.model.__name__} by id: {e}",
                exc_info=True
            )
            raise

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ModelType]:
        """
        Get all entities with optional pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of entities
        """
        try:
            query = self.session.query(self.model)

            if offset is not None:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            entities = query.all()

            self.logger.debug(
                f"Retrieved {len(entities)} {self.model.__name__} entities"
            )
            return entities

        except Exception as e:
            self.logger.error(
                f"Error getting all {self.model.__name__}: {e}",
                exc_info=True
            )
            raise

    def update(
        self,
        entity_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update an entity.

        Args:
            entity_id: Entity ID
            updates: Dictionary of fields to update

        Returns:
            Updated entity or None if not found

        Raises:
            Exception: If update fails
        """
        try:
            entity = self.get_by_id(entity_id)

            if not entity:
                self.logger.warning(
                    f"{self.model.__name__} not found for update: {entity_id}"
                )
                return None

            # Update fields
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            self.session.commit()
            self.session.refresh(entity)

            self.logger.info(
                f"Updated {self.model.__name__} with id: {entity_id}"
            )
            return entity

        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error updating {self.model.__name__}: {e}",
                exc_info=True
            )
            raise

    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If delete fails
        """
        try:
            entity = self.get_by_id(entity_id)

            if not entity:
                self.logger.warning(
                    f"{self.model.__name__} not found for delete: {entity_id}"
                )
                return False

            self.session.delete(entity)
            self.session.commit()

            self.logger.info(
                f"Deleted {self.model.__name__} with id: {entity_id}"
            )
            return True

        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error deleting {self.model.__name__}: {e}",
                exc_info=True
            )
            raise

    def find_by_filters(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ModelType]:
        """
        Find entities matching filters.

        Args:
            filters: Dictionary of field:value pairs
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching entities
        """
        try:
            query = self.session.query(self.model)

            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

            # Apply pagination
            if offset is not None:
                query = query.offset(offset)

            if limit is not None:
                query = query.limit(limit)

            entities = query.all()

            self.logger.debug(
                f"Found {len(entities)} {self.model.__name__} "
                f"matching filters: {filters}"
            )
            return entities

        except Exception as e:
            self.logger.error(
                f"Error finding {self.model.__name__} by filters: {e}",
                exc_info=True
            )
            raise

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities matching optional filters.

        Args:
            filters: Optional dictionary of filters

        Returns:
            Count of matching entities
        """
        try:
            query = self.session.query(self.model)

            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)

            count = query.count()

            self.logger.debug(
                f"Counted {count} {self.model.__name__} entities"
            )
            return count

        except Exception as e:
            self.logger.error(
                f"Error counting {self.model.__name__}: {e}",
                exc_info=True
            )
            raise

    def exists(self, entity_id: str) -> bool:
        """
        Check if entity exists.

        Args:
            entity_id: Entity ID

        Returns:
            True if exists, False otherwise
        """
        try:
            exists = self.session.query(
                self.session.query(self.model).filter(
                    self.model.id == entity_id
                ).exists()
            ).scalar()

            return bool(exists)

        except Exception as e:
            self.logger.error(
                f"Error checking {self.model.__name__} exists: {e}",
                exc_info=True
            )
            raise

    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple entities in bulk.

        Args:
            data_list: List of data dictionaries

        Returns:
            List of created entities

        Raises:
            Exception: If bulk creation fails
        """
        try:
            entities = [self.model(**data) for data in data_list]
            self.session.add_all(entities)
            self.session.commit()

            # Refresh all entities
            for entity in entities:
                self.session.refresh(entity)

            self.logger.info(
                f"Bulk created {len(entities)} {self.model.__name__} entities"
            )
            return entities

        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error bulk creating {self.model.__name__}: {e}",
                exc_info=True
            )
            raise

    def bulk_delete(self, entity_ids: List[str]) -> int:
        """
        Delete multiple entities in bulk.

        Args:
            entity_ids: List of entity IDs

        Returns:
            Number of entities deleted

        Raises:
            Exception: If bulk delete fails
        """
        try:
            deleted_count = self.session.query(self.model).filter(
                self.model.id.in_(entity_ids)
            ).delete(synchronize_session=False)

            self.session.commit()

            self.logger.info(
                f"Bulk deleted {deleted_count} {self.model.__name__} entities"
            )
            return deleted_count

        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error bulk deleting {self.model.__name__}: {e}",
                exc_info=True
            )
            raise

    def refresh(self, entity: ModelType) -> ModelType:
        """
        Refresh entity from database.

        Args:
            entity: Entity to refresh

        Returns:
            Refreshed entity
        """
        self.session.refresh(entity)
        return entity

    def commit(self) -> None:
        """Commit the current transaction."""
        try:
            self.session.commit()
            self.logger.debug("Transaction committed")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error committing transaction: {e}", exc_info=True)
            raise

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()
        self.logger.debug("Transaction rolled back")
