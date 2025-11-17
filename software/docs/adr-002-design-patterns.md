# ADR-002: Design Patterns

## Status
Accepted

## Context
We need to structure the codebase to support:
- User actions (play, pause, stop, etc.)
- State change notifications (for UI, LEDs, logging)
- Swappable audio backends
- Future undo/redo functionality

## Decision
We will use three primary design patterns:

1. **Command Pattern** for user actions
2. **Observer Pattern** for state change notifications
3. **Strategy/Adapter Pattern** for audio backends

## Command Pattern

### Implementation
- Base `Command` interface in `application/commands/base_command.py`
- Concrete commands: `PlayCommand`, `PauseCommand`, `StopCommand`, `NextCommand`, `PrevCommand`

### Rationale
- Encapsulates actions as objects
- Enables future undo/redo
- Allows command queuing and macros
- Supports logging and auditing

### Example
```python
command = PlayCommand(player_service)
command.execute()
```

## Observer Pattern

### Implementation
- `Observer` and `Subject` interfaces in `domain/interfaces/observer.py`
- `PlayerService` extends `Subject`
- Concrete observers: `LoggingObserver`, `LEDObserver`

### Rationale
- Decouples state changes from reactions
- Multiple observers can react to same event
- Easy to add new observers (GUI, analytics, etc.)

### Example
```python
player_service.attach(logging_observer)
player_service.attach(led_observer)
player_service.play()  # Both observers notified
```

## Strategy/Adapter Pattern

### Implementation
- `AudioPlayerInterface` in `domain/interfaces/audio_player.py`
- `LocalFileAudioPlayer` implements interface using VLC
- Future: `HardwareAudioPlayer`, `NetworkAudioPlayer`

### Rationale
- Easy to swap audio backends
- Testable with mock implementations
- Supports different hardware configurations

### Example
```python
# Can swap implementations without changing application code
audio_player = LocalFileAudioPlayer()  # or HardwareAudioPlayer()
player_service = PlayerService(audio_player)
```

## Consequences

### Positive
- Commands can be queued, logged, and undone
- Observers can be added/removed dynamically
- Audio backends can be swapped at runtime
- All patterns support testing with mocks

### Negative
- Some indirection (commands wrap simple method calls)
- Observer management adds complexity
- Interface abstractions require more code

## Alternatives Considered

### Direct Method Calls
- **Rejected**: No undo/redo, harder to test, no command queuing

### Callback Functions
- **Rejected**: Less flexible than observer pattern, harder to manage multiple callbacks

### Hard-coded Audio Backend
- **Rejected**: Not testable, can't swap implementations, tightly coupled

## Future Extensions

- **Command History**: Store commands for undo/redo
- **Command Macros**: Combine multiple commands
- **Event Sourcing**: Store all state changes as events
- **Plugin System**: Allow third-party observers and commands





