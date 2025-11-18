# Repository Structure

This document provides an overview of the complete repository structure for Playt Player.

## Directory Tree

```
software/
├── .gitignore                 # Git ignore rules
├── .python-version           # Python version specification
├── pyproject.toml            # Poetry configuration and dependencies
├── README.md                 # Main project documentation
├── ROADMAP.md               # Development roadmap
├── REPOSITORY_STRUCTURE.md  # This file
│
├── playt_player/            # Main package
│   ├── __init__.py
│   │
│   ├── domain/              # Domain layer (business logic)
│   │   ├── __init__.py
│   │   ├── entities/        # Domain entities
│   │   │   ├── __init__.py
│   │   │   ├── album.py    # Album entity
│   │   │   ├── cartridge.py # Cartridge entity
│   │   │   ├── library.py  # Library entity
│   │   │   └── song.py     # Song entity
│   │   ├── interfaces/      # Abstract interfaces
│   │   │   ├── __init__.py
│   │   │   ├── audio_player.py      # Audio player interface
│   │   │   ├── cartridge_reader.py  # Cartridge reader interface
│   │   │   └── observer.py          # Observer pattern interfaces
│   │   └── services/        # Domain services (stub)
│   │       └── __init__.py
│   │
│   ├── application/         # Application layer (use cases)
│   │   ├── __init__.py
│   │   ├── commands/        # Command pattern implementations
│   │   │   ├── __init__.py
│   │   │   ├── base_command.py
│   │   │   ├── next_command.py
│   │   │   ├── pause_command.py
│   │   │   ├── play_command.py
│   │   │   ├── prev_command.py
│   │   │   └── stop_command.py
│   │   └── player_service.py # Main player service
│   │
│   ├── infrastructure/      # Infrastructure layer (external)
│   │   ├── __init__.py
│   │   ├── audio/           # Audio implementations
│   │   │   ├── __init__.py
│   │   │   └── ffmpeg_audio_player.py  # FFmpeg-based player
│   │   ├── cartridge/       # Cartridge implementations
│   │   │   ├── __init__.py
│   │   │   └── local_file_cartridge_reader.py
│   │   └── observers/       # Observer implementations
│   │       ├── __init__.py
│   │       ├── led_observer.py      # LED feedback (stub)
│   │       └── logging_observer.py   # Logging observer
│   │
│   └── interface/           # Interface layer (UI)
│       ├── __init__.py
│       └── cli/            # Command-line interface
│           ├── __init__.py
│           └── player_cli.py
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Pytest configuration
│   ├── unit/               # Unit tests
│   │   ├── __init__.py
│   │   ├── test_album.py
│   │   ├── test_commands.py
│   │   ├── test_library.py
│   │   ├── test_observer.py
│   │   ├── test_player_service.py
│   │   └── test_song.py
│   └── integration/        # Integration tests
│       ├── __init__.py
│       └── test_player_integration.py
│
├── docs/                    # Documentation
│   ├── architecture.md              # Architecture documentation
│   ├── adr-001-clean-architecture.md # Architecture decision record
│   └── adr-002-design-patterns.md   # Design patterns ADR
│
├── sample_data/             # Sample data for testing
│   └── cartridges/
│       └── test_album/
│           └── metadata.json
│
└── scripts/                 # Utility scripts
    └── verify_setup.py      # Setup verification script
```

## Key Files

### Configuration
- `pyproject.toml`: Poetry configuration, dependencies, and tool settings (black, ruff, mypy, pytest)

### Domain Layer
- `domain/entities/`: Core business entities (Song, Album, Library, Cartridge)
- `domain/interfaces/`: Abstract interfaces for dependency inversion

### Application Layer
- `application/player_service.py`: Main orchestration service
- `application/commands/`: Command pattern implementations

### Infrastructure Layer
- `infrastructure/audio/`: Audio playback implementations
- `infrastructure/cartridge/`: Cartridge reading implementations
- `infrastructure/observers/`: Observer implementations

### Tests
- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: End-to-end integration tests

### Documentation
- `README.md`: User-facing documentation
- `docs/architecture.md`: Technical architecture documentation
- `ROADMAP.md`: Development roadmap and milestones
- `docs/adr-*.md`: Architecture Decision Records

## Design Patterns Used

1. **Command Pattern**: `application/commands/`
2. **Observer Pattern**: `domain/interfaces/observer.py` + `infrastructure/observers/`
3. **Strategy/Adapter Pattern**: Interfaces in `domain/interfaces/`, implementations in `infrastructure/`

## Architecture Layers

1. **Domain**: No dependencies on other layers
2. **Application**: Depends only on domain
3. **Infrastructure**: Depends on domain and application
4. **Interface**: Depends on application and infrastructure

## Entry Points

- CLI: `playt_player.interface.cli.player_cli:main`
- Poetry script: `playt` command (defined in pyproject.toml)

## Testing

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Coverage target: 90%+
- Run tests: `poetry run pytest`

## Code Quality

- Formatting: Black (configured in pyproject.toml)
- Linting: Ruff (configured in pyproject.toml)
- Type checking: mypy strict mode (configured in pyproject.toml)






