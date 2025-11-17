# ADR-001: Clean Architecture

## Status
Accepted

## Context
We need to build a long-term, extensible audio player application that will integrate with physical hardware (NFC readers, LEDs, buttons) and support multiple interfaces (CLI, GUI, web). The codebase must be maintainable, testable, and allow for easy extension without breaking existing functionality.

## Decision
We will adopt **Clean Architecture** (also known as Hexagonal Architecture or Ports and Adapters) as the primary architectural pattern.

## Architecture Layers

1. **Domain Layer**: Core business entities and interfaces (no external dependencies)
2. **Application Layer**: Use cases and orchestration (depends only on domain)
3. **Infrastructure Layer**: External integrations (depends on domain/application)
4. **Interface Layer**: User interfaces (depends on application/infrastructure)

## Rationale

### Benefits
- **Testability**: Business logic isolated from external dependencies
- **Flexibility**: Easy to swap implementations (audio backends, storage, UI)
- **Maintainability**: Clear separation of concerns
- **Extensibility**: New features don't require modifying existing code
- **Independence**: Domain logic independent of frameworks and libraries

### Trade-offs
- **Initial Complexity**: More files and structure than a simple script
- **Learning Curve**: Team needs to understand layer boundaries
- **Overhead**: Some boilerplate for dependency injection

## Consequences

### Positive
- Easy to add new audio backends without changing application code
- Business logic can be tested without actual audio playback
- Hardware integration can be added without modifying core logic
- Multiple UIs can share the same application layer

### Negative
- More files and directories to navigate
- Requires discipline to maintain layer boundaries
- Some indirection (interfaces) may seem unnecessary for simple cases

## Implementation Notes

- All domain interfaces defined in `domain/interfaces/`
- Concrete implementations in `infrastructure/`
- Dependency injection through constructors
- No circular dependencies between layers

## Alternatives Considered

### Monolithic Structure
- **Rejected**: Hard to test, tightly coupled, difficult to extend

### MVC Pattern
- **Rejected**: Too UI-focused, doesn't address business logic isolation

### Layered Architecture (Traditional)
- **Rejected**: Infrastructure layer would depend on application, violating dependency rule

## References
- Clean Architecture by Robert C. Martin
- Hexagonal Architecture by Alistair Cockburn




