# Kitsu Home Studio

A toolkit for Kitsu pipeline integration with various DCC software.

## Features

- Task management interface for Kitsu
- Integration with multiple DCC software:
  - DaVinci Resolve
  - Krita
  - Nuke (coming soon)
- Project and task context management
- User authentication and session management

## Installation

```bash
pip install kitsu-home-studio
```

## Usage

### Task Manager

Run the task manager:

```bash
kitsu-task-manager
```

### Software Integration

The toolkit provides integration with various DCC software. Each integration follows a common interface:

```python
from kitsu_home_studio.integrations.resolve import ResolveIntegration
from kitsu_home_studio.integrations.krita import KritaIntegration

# Create integration instance
resolve = ResolveIntegration(software_path="path/to/resolve.exe")

# Launch software with task context
resolve.launch(task_context)

# Publish work to Kitsu
resolve.publish(task_context)
```

## Project Structure

```
kitsu_home_studio/
├── core/                      # Core Kitsu functionality
│   ├── auth.py               # Authentication and connection handling
│   └── api.py                # Kitsu API interactions
│
├── integrations/             # Software-specific integrations
│   ├── base.py              # Base integration class/interface
│   ├── resolve/             # DaVinci Resolve integration
│   ├── krita/               # Krita integration
│   └── nuke/                # Nuke integration
│
├── ui/                      # UI components
│   ├── task_manager/        # Task manager UI
│   └── common/              # Shared UI components
│
└── utils/                   # General utilities
    └── file_utils.py        # File operations
```

## Development

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kitsu-home-studio.git
cd kitsu-home-studio
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 