# CLAUDE.md - Guidelines for taiga_to_bpm project

## Build/Test Commands
- Install dependencies: `pip install -e .` or `poetry install`
- Run all tests: `python -m pytest`
- Run single test: `python -m pytest tests/test_file.py::test_function_name`
- Type checking: `mypy .`
- Lint code: `ruff check .`
- Format code: `ruff format .`

## Code Style Guidelines
- **Imports**: Group by stdlib, third-party, first-party with headers
- **Formatting**: Line length 60, use trailing commas in multi-line imports
- **Types**: Use Python 3.12+ typing, Pydantic for models
- **Naming**: Use snake_case for functions/variables, PascalCase for classes
- **Error Handling**: Use explicit try/except blocks with specific exceptions
- **State Management**: Use Redis for temporary state, PostgreSQL for persistence
- **Testing**: Use pytest, TUser context manager for bot tests

## Project Structure
- `bot_interface/`: Telegram bot implementation
- `db/`: Database connectivity and queries
- `core/`: Shared models and business logic
- `taiga_to_bpm/`: Integration with BPM system