# Finance Analyzer

A professional desktop application for analyzing and categorizing financial transactions from Excel files.

## Features

- **Excel File Import**: Load and process financial data from Excel files
- **Automatic Categorization**: Smart categorization based on transaction descriptions
- **Advanced Filtering**: Filter by category, search terms, and transaction values (positive/negative)
- **Interactive Charts**: Visual representation of category summaries with multi-color system
- **Data Export**: Export processed data to Excel format
- **Keyword Learning**: Save and reuse categorization rules
- **Fullscreen Interface**: Modern, responsive UI optimized for data analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (tested on Windows 10)

### Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## Building the Executable

### Automatic Build

Use the provided build script:

```bash
python build_exe.py
```

### Manual Build

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Build using the spec file:

   ```bash
   pyinstaller finance_analyzer.spec
   ```

3. The executable will be created in the `dist` folder.

## Usage

1. **Load Data**: Click "Load File" to select an Excel file with financial data
2. **Analyze**: Click "Analyze" to automatically categorize transactions
3. **Review**: Use filters to review and edit categorizations
4. **Export**: Save processed data or keywords for future use

## Project Structure

```
finance-analyzer-app/
├── main.py                 # Application entry point
├── gui/                    # User interface components
│   ├── app_ui.py          # Main application window
│   └── frames/            # UI frame components
├── core/                   # Core business logic
│   ├── controller.py      # Application controller
│   ├── data_processor.py  # Data processing utilities
│   └── data_utils.py      # Data manipulation functions
├── config/                 # Configuration files
│   ├── categories_list.txt # Available categories
│   └── keywords.json      # Categorization rules
├── models/                 # Data models
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── finance_analyzer.spec   # PyInstaller configuration
└── build_exe.py           # Build automation script
```

## Configuration

### Categories

Edit `config/categories_list.txt` to customize available categories:

```
Income
Food & Groceries
Transport
Housing_Expense
...
```

### Keywords

The application automatically learns categorization rules and saves them to `config/keywords.json`.

## Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) folder:

- **Bug Fixes & Improvements**: Detailed documentation of all fixes and enhancements
- **Build Instructions**: Step-by-step guide for creating executables
- **Feature Documentation**: Complete feature descriptions and usage guides

See [`docs/README.md`](./docs/README.md) for a complete documentation index.

## Troubleshooting

### Common Issues

1. **Matplotlib not working in executable**

   - Ensure matplotlib is installed: `pip install matplotlib`
   - The application includes fallback handling for missing matplotlib

2. **Config files not found**

   - Ensure the `config` folder is included in the executable
   - Check that file paths are correctly resolved

3. **Excel file loading issues**
   - Ensure openpyxl is installed: `pip install openpyxl`
   - Check Excel file format compatibility

### Debug Mode

To enable console output for debugging, edit `finance_analyzer.spec`:

```python
console=True,  # Change from False to True
```

## Development

### Code Quality

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes

### Testing

Run tests with:

```bash
python -m pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please check the troubleshooting section or create an issue in the repository.
