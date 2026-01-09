# Contributing to YouTube Thumbnail Extractor Bot

Thank you for considering contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** (if available)
3. **Include details**:
   - Bot version
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Features

1. **Check existing suggestions** first
2. **Explain the use case** clearly
3. **Provide examples** of how it would work
4. **Consider implementation** complexity

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/thumbxtract-telegram-bot.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Write clear commit messages
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   python test_bot.py
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe your changes
   - Reference related issues
   - Explain testing done

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/inyogeshwar/thumbxtract-telegram-bot.git
   cd thumbxtract-telegram-bot
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   ```bash
   cp config.ini.example config.ini
   # Edit config.ini with your test bot token
   ```

5. **Run tests**
   ```bash
   python test_bot.py
   ```

## Code Style Guidelines

### Python Style

Follow PEP 8 guidelines:
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions and classes

Example:
```python
async def process_video_id(video_id: str) -> List[str]:
    """
    Process a YouTube video ID and return thumbnail URLs.
    
    Args:
        video_id: YouTube video ID (11 characters)
        
    Returns:
        List of thumbnail URLs
    """
    if not YouTubeExtractor.validate_video_id(video_id):
        raise ValueError(f"Invalid video ID: {video_id}")
    
    return YouTubeExtractor.get_thumbnails(video_id)
```

### Documentation

- Use clear and concise language
- Include code examples
- Update README.md when adding features
- Add inline comments for complex logic

### Commit Messages

Follow conventional commits:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `test: add tests`
- `refactor: improve code structure`
- `style: fix formatting`

## Project Structure

```
thumbxtract-telegram-bot/
├── bot.py              # Main bot logic
├── database.py         # Database operations
├── youtube_utils.py    # YouTube extraction
├── i18n.py            # Internationalization
├── test_bot.py        # Test suite
├── config.ini.example  # Configuration template
├── requirements.txt    # Dependencies
├── README.md          # Main documentation
├── EXAMPLES.md        # Usage examples
├── DEPLOYMENT.md      # Deployment guide
└── CONTRIBUTING.md    # This file
```

## Adding New Features

### Adding a New Language

1. **Update i18n.py**:
   ```python
   TRANSLATIONS = {
       # ... existing languages
       'de': {  # German
           'welcome': 'Willkommen...',
           # ... all translations
       }
   }
   
   LANGUAGE_NAMES = {
       # ... existing languages
       'de': 'Deutsch 🇩🇪',
   }
   ```

2. **Test the translation**:
   - Verify all keys are present
   - Check text formatting
   - Test language detection

3. **Update documentation**:
   - Add language to README.md
   - Update EXAMPLES.md

### Adding a New Command

1. **Create handler in bot.py**:
   ```python
   async def new_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Handle /newcommand."""
       user_id = update.effective_user.id
       # Implementation
       await update.message.reply_text("Response")
   ```

2. **Register handler**:
   ```python
   application.add_handler(CommandHandler("newcommand", self.new_command))
   ```

3. **Add translations**:
   - Add text keys to all languages in i18n.py

4. **Update documentation**:
   - Add command to README.md
   - Add usage example to EXAMPLES.md

### Adding Database Features

1. **Update schema** in database.py `initialize()`:
   ```python
   await db.execute('''
       CREATE TABLE IF NOT EXISTS new_table (
           id INTEGER PRIMARY KEY,
           -- columns
       )
   ''')
   ```

2. **Add methods**:
   ```python
   async def new_operation(self, param: str) -> bool:
       """Perform new database operation."""
       # Implementation
   ```

3. **Add tests** in test_bot.py

## Testing

### Running Tests

```bash
python test_bot.py
```

### Writing Tests

Add tests to `test_bot.py`:

```python
async def test_new_feature():
    """Test the new feature."""
    # Arrange
    input_data = "test"
    
    # Act
    result = await new_feature(input_data)
    
    # Assert
    assert result == expected_output
    print("✅ New feature test passed")
    return True
```

### Manual Testing

1. Set up a test bot on Telegram
2. Use a test user account
3. Test all commands and features
4. Verify database operations
5. Check error handling

## Documentation

### What to Document

- New features
- API changes
- Breaking changes
- Configuration options
- Usage examples

### Where to Document

- **README.md**: Overview and setup
- **EXAMPLES.md**: Usage examples
- **DEPLOYMENT.md**: Deployment instructions
- **Code comments**: Complex logic
- **Docstrings**: Functions and classes

## Review Process

1. **Automated checks**: Tests must pass
2. **Code review**: Maintainers review code
3. **Documentation review**: Docs must be updated
4. **Testing verification**: Changes must be tested

## Questions?

- Open an issue for questions
- Tag maintainers if needed
- Be patient and respectful

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- README.md (for major features)

Thank you for contributing! 🎉
