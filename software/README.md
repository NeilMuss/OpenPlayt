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
│   ├── commands/        # Command pattern implementation
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
- FFmpeg (specifically `ffplay` for audio playback)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg` (Ubuntu/Debian) or use your distribution's package manager
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add `ffplay.exe` to your PATH

### Setup with pip (recommended if Poetry is not installed)

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate  # On Windows
   ```

2. Navigate to the software directory:
   ```bash
   cd software
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Setup with Poetry (alternative)

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

### Running the Player GUI

#### Load the sample .playt file:
```bash
python run_player.py "sample_data/cartridges/test_album/Lumière Noctae - Échos de Brume.playt"
```

### Running the Player in the Command Line Interface (CLI)

#### Load and play a .playt file:
```bash
python -m playt_player.interface.cli.player_cli /path/to/album.playt
```

#### Load and auto-play:
```bash
python -m playt_player.interface.cli.player_cli /path/to/album.playt --auto-play
```

#### Start interactive CLI (then load a .playt file):
```bash
python -m playt_player.interface.cli.player_cli
```

#### Example: play the provided cartridge
```bash
python -m playt_player.interface.cli.player_cli "sample_data/cartridges/test_album/Lumière Noctae - Échos de Brume.playt"
```

**Note:** If using Poetry, you can use `poetry run` prefix:
```bash
poetry run playt /path/to/album.playt
# OR
poetry run python -m playt_player.interface.cli.player_cli /path/to/album.playt
```

### CLI Commands

- `play` - Start or resume playback
- `pause` - Pause playback
- `stop` - Stop playback
- `next` - Skip to next track
- `prev` - Go to previous track
- `load <path>` - Load album from .playt file (e.g., `load /path/to/album.playt`)
- `status` - Show current status
- `help` - Show help message
- `quit` / `q` - Exit the player

### Loading a .playt File

You can load `.playt` files (zip archives containing audio files):

```bash
python -m playt_player.interface.cli.player_cli album.playt
```

The `.playt` file should be a zip archive with audio files in the top-level folder. Supported audio formats:
- MP3 (`.mp3`)
- FLAC (`.flac`)
- WAV (`.wav`)
- M4A (`.m4a`)
- AAC (`.aac`)
- OGG (`.ogg`)
- Opus (`.opus`)

### Loading a Cartridge (Alternative Format)

Cartridges can also be directories containing:
- `metadata.json` - Cartridge and album metadata
- Audio files referenced in the metadata

**Note:** Direct loading of directory-based cartridges via the CLI `load` command is not yet implemented in the interactive mode. This format is primarily for development and future hardware integration.

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
# With pip:
pytest

# With Poetry:
poetry run pytest
```

Run with coverage report:
```bash
# With pip:
pytest --cov=playt_player --cov-report=html

# With Poetry:
poetry run pytest --cov=playt_player --cov-report=html
```

Run specific test file:
```bash
# With pip:
pytest tests/unit/test_song.py

# With Poetry:
poetry run pytest tests/unit/test_song.py
```

### Code Quality

Install development dependencies first:
```bash
# With pip:
pip install -r requirements-dev.txt

# With Poetry:
poetry install
```

Format code with Black:
```bash
# With pip:
black playt_player tests

# With Poetry:
poetry run black playt_player tests
```

Lint with Ruff:
```bash
# With pip:
ruff check playt_player tests

# With Poetry:
poetry run ruff check playt_player tests
```

Type check with mypy:
```bash
# With pip:
mypy playt_player

# With Poetry:
poetry run mypy playt_player
```

### Pre-commit Checks

Before committing, ensure:
1. All tests pass: `pytest` (or `poetry run pytest`)
2. Code is formatted: `black .` (or `poetry run black .`)
3. No linting errors: `ruff check .` (or `poetry run ruff check .`)
4. Type checking passes: `mypy playt_player` (or `poetry run mypy playt_player`)

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
- Easy swapping of audio engines (ffmpeg, pydub)
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






