# CLAUDE.md - Guidelines for taiga_to_bpm project

## Build/Test Commands
- Install dependencies: `pip install -e .` or `poetry install`
- Run all tests: `python -m pytest`
- Run single test: `python -m pytest tests/test_file.py::test_function_name`
- Type checking: `mypy .`
- Lint code: `ruff check .`
- Format code: `ruff format .`

## Deployment Procedure
- Before deployment, check code quality:
  1. Run `mypy .` to verify type correctness
  2. Run `ruff check .` to verify linting rules
  3. Run `ruff format .` to ensure proper formatting
- Build and push Docker images:
  ```bash
  docker compose build && docker compose push
  ```

## Code Style Guidelines
- **Imports**: Group by stdlib, third-party, first-party with headers
- **Formatting**: Line length 88, use trailing commas in multi-line imports
- **Types**: Use Python 3.12+ typing, Pydantic for models
- **Naming**: Use snake_case for functions/variables, PascalCase for classes
- **Error Handling**: Use explicit try/except blocks with specific exceptions
- **State Management**: Use Redis for temporary state, PostgreSQL for persistence
- **Testing**: Use pytest, TUser context manager for bot tests
- **Logging**: Each class should create its own logger in __init__ rather than receiving it as a parameter. Use descriptive names like `logging.getLogger("class_name")`

## Project Structure
- `bot_interface/`: Telegram bot implementation
- `db/`: Database connectivity and queries
- `core/`: Shared models and business logic
- `taiga_to_bpm/`: Integration with BPM system
- `notification_listener/`: Database notification processor and Telegram notifications

## Design Patterns
- **Interfaces**: Use Protocol classes to define interfaces (e.g., IDataStorage, INotificationSender)
- **Dependency Injection**: Pass dependencies as constructor parameters
- **Factory Functions**: Use factory functions for creating complex objects with dependencies

## Clean Architecture Principles
- **Domain-Driven Design**: Create domain models that represent core business entities
- **Layer Separation**:
  - Domain layer: Contains business entities and rules, independent of external frameworks
  - Application layer: Contains use cases that orchestrate the flow of data and business rules
  - Infrastructure layer: Contains adapters for external services and frameworks
- **Module Structure**:
  - `domain/`: Core business entities and rules, organized by domain concept
    - `<entity>/models.py`: Domain model data classes
    - `<entity>/interfaces.py`: Protocols defining repositories and services
    - `<entity>/usecases.py`: Business logic and use cases
  - `infrastructure/`: Implementations of interfaces defined in domain layer
    - `repositories/`: Data access implementations
    - `<service>/`: Service implementations
  - `application/`: Orchestration of use cases and services
- **Dependency Rule**: Dependencies should point inward, with domain having no dependencies on outer layers
- **Dependency Inversion**: Outer layers depend on abstractions defined in inner layers
- **Single Responsibility**: Each class should have one reason to change
- **Repositories**: Use repository pattern for data access
- **Use Cases**: Define use cases for each business operation
- **Backwards Compatibility**: Create adapter classes for migration from legacy code