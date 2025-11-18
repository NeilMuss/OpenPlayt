# Architecture Documentation

## Overview

Playt Player follows **Clean Architecture** principles, organizing code into layers with clear dependencies and responsibilities. The architecture prioritizes:

- **Separation of Concerns**: Each layer has a single, well-defined responsibility
- **Dependency Inversion**: High-level modules don't depend on low-level modules; both depend on abstractions
- **Testability**: Business logic is isolated from external dependencies
- **Extensibility**: New features can be added without modifying existing code

## Architecture Layers

### Domain Layer (`domain/`)

The innermost layer containing core business logic and entities. This layer has **no dependencies** on other layers.

#### Entities (`domain/entities/`)
- **Song**: Represents a single audio track
- **Album**: Represents a collection of songs
- **Library**: Manages collections of albums with indexing and search
- **Cartridge**: Represents physical media metadata

Entities are pure data structures with minimal behavior. They include:
- Type annotations
- `__repr__` and `__eq__` methods
- No business logic leakage

#### Interfaces (`domain/interfaces/`)
Abstract interfaces defining contracts for implementations:
- **AudioPlayerInterface**: Audio playback operations
- **CartridgeReaderInterface**: Cartridge reading operations
- **Observer**: Observer pattern interface
- **Subject**: Subject pattern interface

### Application Layer (`application/`)

Orchestrates use cases and coordinates between domain entities and infrastructure.

#### Commands (`application/commands/`)
Command pattern implementations:
- **PlayCommand**: Start/resume playback
- **PauseCommand**: Pause playback
- **StopCommand**: Stop playback
- **NextCommand**: Skip to next track
- **PrevCommand**: Go to previous track

#### Services (`application/`)
- **PlayerService**: Coordinates playback, queue management, and state notifications

### Infrastructure Layer (`infrastructure/`)

Concrete implementations of domain interfaces and external integrations.

#### Audio (`infrastructure/audio/`)
- **LocalFileAudioPlayer**: VLC-based audio playback implementation

#### Cartridge (`infrastructure/cartridge/`)
- **LocalFileCartridgeReader**: Filesystem-based cartridge reader

#### Observers (`infrastructure/observers/`)
- **LoggingObserver**: Logs state changes
- **LEDObserver**: Stub for future hardware LED control

### Interface Layer (`interface/`)

User-facing interfaces and entry points.

#### CLI (`interface/cli/`)
- **PlayerCLI**: Interactive command-line interface

## Dependency Flow

```
Interface Layer
    ↓ depends on
Application Layer
    ↓ depends on
Domain Layer (interfaces)
    ↑ implemented by
Infrastructure Layer
```

**Key Principle**: Dependencies point inward. Outer layers depend on inner layers, but inner layers never depend on outer layers.

## Design Patterns

### Command Pattern

**Purpose**: Encapsulate user actions as objects

**Benefits**:
- Undo/redo support (future)
- Command queuing
- Macro operations
- Logging and auditing

**Implementation**: `application/commands/`

### Observer Pattern

**Purpose**: Notify multiple components of state changes

**Benefits**:
- Decoupled communication
- Multiple observers per event
- Easy to add new observers (LED, GUI, logging)

**Implementation**: `domain/interfaces/observer.py` and `infrastructure/observers/`

### Strategy/Adapter Pattern

**Purpose**: Allow swapping of implementations

**Benefits**:
- Easy to change audio backends
- Testability with mocks
- Future hardware-specific implementations

**Implementation**: Interfaces in `domain/interfaces/`, implementations in `infrastructure/`

## Data Flow

### Playback Flow

1. User issues command (CLI)
2. Command object created (`PlayCommand`)
3. Command executes on `PlayerService`
4. `PlayerService` calls `AudioPlayerInterface`
5. State change triggers observer notifications
6. Observers react (logging, LED, GUI updates)

### Cartridge Loading Flow

1. User requests cartridge load
2. `CartridgeReaderInterface` reads metadata
3. Album entity created from metadata
4. `PlayerService` loads album into queue
5. Observers notified of album load

## Extension Points

### Adding a New Audio Backend

1. Implement `AudioPlayerInterface` in `infrastructure/audio/`
2. Update factory/DI configuration
3. No changes needed to application or domain layers

### Adding Hardware Integration

1. Implement `Observer` interface for hardware feedback
2. Register observer with `PlayerService`
3. Hardware reacts to state change events

### Adding a New Command

1. Create command class in `application/commands/`
2. Implement `Command` interface
3. Wire into CLI or other interface

## Testing Strategy

### Unit Tests
- Test entities in isolation
- Test services with mocked dependencies
- Test commands independently

### Integration Tests
- Test complete workflows
- Use mock implementations for external dependencies
- Verify observer notifications

### Test Doubles
- **Mocks**: For audio player (no actual playback)
- **Stubs**: For file I/O operations
- **Fakes**: For cartridge readers (in-memory)

## Future Considerations

### Hardware Integration
- NFC reader for cartridge detection
- LED controller for visual feedback
- Physical button handlers

### GUI Integration
- WebSocket server for web UI
- Desktop GUI framework
- Mobile app API

### Advanced Features
- Playlist management
- Shuffle and repeat modes
- Equalizer
- Audio effects

All future features should follow the same architectural principles and layer boundaries.






