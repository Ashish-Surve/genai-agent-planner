# ADHD-4: Base Repository Pattern

## Story Information

- **Epic**: Foundation
- **Story Points**: 2
- **Estimated Time**: 2 hours
- **Prerequisites**: ADHD-2 (Database Schema), ADHD-3 (Pydantic Models)
- **Status**: 📋 Not Started

## Description

Implement the base repository pattern that provides generic CRUD operations and query helpers for all entities. This abstraction layer separates data access logic from business logic and makes the codebase more maintainable and testable.

## Goals

1. Create generic base repository with CRUD operations
2. Implement query helper methods
3. Add transaction management
4. Implement error handling and logging
5. Create type-safe methods with generics
6. Add filtering and sorting capabilities
7. Support pagination

## Acceptance Criteria

- [ ] Base repository created with generic type support
- [ ] All CRUD operations work correctly
- [ ] Query helpers handle edge cases
- [ ] Transactions commit and rollback properly
- [ ] Errors are logged and handled gracefully
- [ ] Type hints are complete
- [ ] Unit tests pass

## Files to Create

```
src/repositories/__init__.py
src/repositories/base_repository.py      # Generic base repository
tests/unit/test_base_repository.py       # Repository tests
```

## Implementation Steps

### Step 1: Base Repository Implementation (90 min)

**File**: `src/repositories/base_repository.py`

```python
"""Base repository with generic CRUD operations."""

from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.database.schema import Base
from src.utils.logger import get_logger

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
```

### Step 2: Repository __init__ (5 min)

**File**: `src/repositories/__init__.py`

```python
"""Repository layer for data access."""

from src.repositories.base_repository import BaseRepository

__all__ = ["BaseRepository"]
```

### Step 3: Unit Tests (25 min)

**File**: `tests/unit/test_base_repository.py`

```python
"""Test base repository."""

import pytest
from src.repositories.base_repository import BaseRepository
from src.database.schema import TaskModel


@pytest.fixture
def task_repository(test_db_session):
    """Create task repository for testing."""
    return BaseRepository(TaskModel, test_db_session)


def test_create(task_repository):
    """Test creating an entity."""
    data = {
        "title": "Test task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH"
    }

    task = task_repository.create(data)

    assert task.id is not None
    assert task.title == "Test task"
    assert task.estimated_duration_minutes == 30


def test_get_by_id(task_repository):
    """Test getting entity by ID."""
    # Create task
    data = {
        "title": "Test task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH"
    }
    task = task_repository.create(data)

    # Get by ID
    retrieved = task_repository.get_by_id(task.id)

    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.title == task.title


def test_get_by_id_not_found(task_repository):
    """Test getting non-existent entity."""
    result = task_repository.get_by_id("non-existent-id")
    assert result is None


def test_get_all(task_repository):
    """Test getting all entities."""
    # Create multiple tasks
    for i in range(5):
        task_repository.create({
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH"
        })

    # Get all
    tasks = task_repository.get_all()
    assert len(tasks) == 5


def test_get_all_with_pagination(task_repository):
    """Test pagination."""
    # Create tasks
    for i in range(10):
        task_repository.create({
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH"
        })

    # Get with limit
    tasks = task_repository.get_all(limit=5)
    assert len(tasks) == 5

    # Get with offset
    tasks = task_repository.get_all(limit=5, offset=5)
    assert len(tasks) == 5


def test_update(task_repository):
    """Test updating an entity."""
    # Create task
    task = task_repository.create({
        "title": "Original title",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH"
    })

    # Update
    updated = task_repository.update(task.id, {
        "title": "Updated title",
        "estimated_duration_minutes": 45
    })

    assert updated.title == "Updated title"
    assert updated.estimated_duration_minutes == 45


def test_update_not_found(task_repository):
    """Test updating non-existent entity."""
    result = task_repository.update("non-existent-id", {"title": "New"})
    assert result is None


def test_delete(task_repository):
    """Test deleting an entity."""
    # Create task
    task = task_repository.create({
        "title": "Test task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH"
    })

    # Delete
    success = task_repository.delete(task.id)
    assert success is True

    # Verify deleted
    result = task_repository.get_by_id(task.id)
    assert result is None


def test_delete_not_found(task_repository):
    """Test deleting non-existent entity."""
    success = task_repository.delete("non-existent-id")
    assert success is False


def test_find_by_filters(task_repository):
    """Test finding entities by filters."""
    # Create tasks with different priorities
    task_repository.create({
        "title": "High priority task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH"
    })
    task_repository.create({
        "title": "Low priority task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "LOW"
    })

    # Find by filter
    high_priority = task_repository.find_by_filters({"priority": "HIGH"})
    assert len(high_priority) == 1
    assert high_priority[0].title == "High priority task"


def test_count(task_repository):
    """Test counting entities."""
    # Create tasks
    for i in range(7):
        task_repository.create({
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH"
        })

    # Count all
    count = task_repository.count()
    assert count == 7

    # Count with filter
    count = task_repository.count({"priority": "HIGH"})
    assert count == 7


def test_exists(task_repository):
    """Test checking if entity exists."""
    # Create task
    task = task_repository.create({
        "title": "Test task",
        "estimated_duration_minutes": 30,
        "estimated_energy_level": "MEDIUM",
        "priority": "HIGH"
    })

    # Check exists
    assert task_repository.exists(task.id) is True
    assert task_repository.exists("non-existent-id") is False


def test_bulk_create(task_repository):
    """Test bulk creation."""
    data_list = [
        {
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH"
        }
        for i in range(5)
    ]

    tasks = task_repository.bulk_create(data_list)

    assert len(tasks) == 5
    assert all(task.id is not None for task in tasks)


def test_bulk_delete(task_repository):
    """Test bulk deletion."""
    # Create tasks
    tasks = task_repository.bulk_create([
        {
            "title": f"Task {i}",
            "estimated_duration_minutes": 30,
            "estimated_energy_level": "MEDIUM",
            "priority": "HIGH"
        }
        for i in range(5)
    ])

    # Get IDs
    task_ids = [task.id for task in tasks]

    # Bulk delete
    deleted_count = task_repository.bulk_delete(task_ids)

    assert deleted_count == 5

    # Verify all deleted
    for task_id in task_ids:
        assert task_repository.get_by_id(task_id) is None
```

## Testing Checklist

```bash
# 1. Run unit tests
uv run pytest tests/unit/test_base_repository.py -v

# 2. Test repository creation
uv run python -c "
from src.database.connection import get_db
from src.database.schema import TaskModel
from src.repositories.base_repository import BaseRepository

db = get_db()
with db.get_session() as session:
    repo = BaseRepository(TaskModel, session)
    print(f'Repository created for: {repo.model.__name__}')
"

# 3. Test CRUD operations
uv run python -c "
from src.database.connection import get_db
from src.database.schema import TaskModel
from src.repositories.base_repository import BaseRepository

db = get_db()
with db.get_session() as session:
    repo = BaseRepository(TaskModel, session)

    # Create
    task = repo.create({
        'title': 'Test task',
        'estimated_duration_minutes': 30,
        'estimated_energy_level': 'MEDIUM',
        'priority': 'HIGH'
    })
    print(f'Created: {task.id}')

    # Read
    found = repo.get_by_id(task.id)
    print(f'Found: {found.title}')

    # Update
    updated = repo.update(task.id, {'title': 'Updated task'})
    print(f'Updated: {updated.title}')

    # Delete
    repo.delete(task.id)
    print('Deleted')
"

# 4. Run all tests
uv run pytest tests/unit/ -v

# 5. Code quality
uv run ruff check src/repositories/
uv run black --check src/repositories/
```

## Success Criteria

- ✅ Base repository created with generics
- ✅ All CRUD operations work
- ✅ Query helpers handle edge cases
- ✅ Transactions handled properly
- ✅ Errors logged correctly
- ✅ All unit tests pass
- ✅ Code quality checks pass

## Common Issues & Solutions

### Issue: Type hints not working correctly
**Solution**: Ensure Python 3.10+ for proper generic support

### Issue: Session commit conflicts
**Solution**: Repository commits by default, services can manage transactions

### Issue: Refresh failing after create
**Solution**: Ensure session is still active when refreshing

## Next Story

Once this story is complete, move to:
**[ADHD-5: Task & TimeBlock Repositories](ADHD-5-task-timeblock-repositories.md)**

## Notes

- Base repository provides the foundation for all data access
- Generic typing ensures type safety across all repositories
- Transaction management can be overridden by services when needed
- Logging at repository level helps debug data access issues
- Keep repository focused on data access - business logic belongs in services
- Bulk operations improve performance for large datasets
