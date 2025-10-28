# Contributing to InsightForge

Thank you for your interest in contributing to InsightForge! 🎉

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/insightforge.git
cd insightforge

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start services
docker compose up -d

# Run tests
pytest
```

## Code Style

### Python
- Use **Black** for formatting
- Follow **PEP 8**
- Add type hints
- Write docstrings

### JavaScript/TypeScript
- Use **Prettier** for formatting
- Follow **ESLint** rules
- Use TypeScript types

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add new feature
fix: fix bug
docs: update documentation
style: formatting changes
refactor: code refactoring
test: add tests
chore: maintenance
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review

## Questions?

Open an issue or start a discussion!
