# Playt Player

A clean architecture audio player application designed for physical media cartridges with extensible design, test-driven development, and SOLID principles.

## Overview

Playt Player is a Python-based audio player built with clean architecture principles, designed to eventually work with physical media cartridges that include metadata in JSON format. The codebase prioritizes maintainability, extensibility, modularity, testability, and dependency injection.

## Features

- **Clean Architecture**: Layered architecture with clear separation of concerns
- **SOLID Principles**: Interface-based design with dependency injection
- **Design Patterns**: Observer, Command, and Strategy/Adapter patterns
- **Type Safety**: Full type annotations with mypy strict mode
- **Test-Driven Development**: Comprehensive test suite with 90%+ coverage target
- **Extensible Design**: Ready for hardware integration (NFC, LEDs, GUI skins)

## Project Structure

```
playt_player/
├── domain/              # Core business logic and entities
│   ├── entities/        # Domain models (Song, Album, Library)
│   └── interfaces/      # Abstract interfaces (AudioPlayer, Observer, etc.)
├── application/         # Use cases and orchestration
│   ├── commands/        # Command pattern implementations
│   └── player_service.py
├── infrastructure/      # External integrations
│   ├── audio/           # Audio player implementations
│   ├── cartridge/       # Cartridge reader implementations
│   └── observers/       # Observer implementations
└── interface/           # User interfaces
    └── cli/             # Command-line interface

tests/
├── unit/                # Unit tests
└── integration/         # Integration tests
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)

### Setup

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Navigate to the software directory:
   ```bash
   cd software
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Usage

### Running the Player

Start the interactive CLI:
```bash
poetry run playt
```

Or use Python directly:
```bash
poetry run python -m playt_player.interface.cli.player_cli
```

### CLI Commands

- `play` - Start or resume playback
- `pause` - Pause playback
- `stop` - Stop playback
- `next` - Skip to next track
- `prev` - Go to previous track
- `load <cartridge_id>` - Load album from cartridge
- `status` - Show current status
- `help` - Show help message
- `quit` / `q` - Exit the player

### Loading a Cartridge

Cartridges are directories containing:
- `metadata.json` - Cartridge and album metadata
- Audio files referenced in the metadata

Example cartridge structure:
```
cartridges/
  test_album/
    metadata.json
    01_opening_track.mp3
    02_midnight_drive.mp3
    03_closing_theme.mp3
```

See `sample_data/cartridges/test_album/metadata.json` for an example metadata file.

## Development

### Running Tests

Run all tests:
```bash
poetry run pytest
```

Run with coverage report:
```bash
poetry run pytest --cov=playt_player --cov-report=html
```

Run specific test file:
```bash
poetry run pytest tests/unit/test_song.py
```

### Code Quality

Format code with Black:
```bash
poetry run black playt_player tests
```

Lint with Ruff:
```bash
poetry run ruff check playt_player tests
```

Type check with mypy:
```bash
poetry run mypy playt_player
```

### Pre-commit Checks

Before committing, ensure:
1. All tests pass: `poetry run pytest`
2. Code is formatted: `poetry run black .`
3. No linting errors: `poetry run ruff check .`
4. Type checking passes: `poetry run mypy playt_player`

## Architecture

The application follows clean architecture principles:

- **Domain Layer**: Core business entities and interfaces (no dependencies on other layers)
- **Application Layer**: Use cases and orchestration (depends only on domain)
- **Infrastructure Layer**: External integrations (depends on domain and application)
- **Interface Layer**: User interfaces (depends on application and infrastructure)

See `docs/architecture.md` for detailed architecture documentation.

## Design Patterns

### Command Pattern
User actions (play, pause, stop, etc.) are encapsulated as command objects, allowing for:
- Undo/redo functionality (future)
- Command queuing
- Macro operations
- Logging and auditing

### Observer Pattern
State changes are broadcast to registered observers, enabling:
- UI updates
- LED feedback (future hardware integration)
- Logging and monitoring
- Analytics

### Strategy/Adapter Pattern
Audio playback backends are abstracted through interfaces, allowing:
- Easy swapping of audio engines (VLC, ffmpeg, pydub)
- Testing with mock implementations
- Future hardware-specific implementations

## Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows end-to-end
- **Mock Objects**: Use mocks for external dependencies (audio playback, file I/O)
- **Coverage Target**: 90% code coverage

## Roadmap

See `ROADMAP.md` for detailed development milestones and future features.

## Contributing

1. Follow the existing code structure and patterns
2. Write tests for new features (TDD approach)
3. Ensure all tests pass and coverage remains above 90%
4. Run code quality tools before committing
5. Update documentation as needed

## License

See LICENSE files in the project root.

## Support

For issues, questions, or contributions, please refer to the project documentation or create an issue in the repository.





