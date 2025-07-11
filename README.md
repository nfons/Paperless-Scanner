# Paperless Scanner

A desktop application that streamlines the process of scanning documents and uploading them to Paperless-ngx. Tired of having to scan papers, then login to paperless, and then upload, and then delete the scanned doc? This app does it all for you in one seamless workflow.

## Features

- **One-Click Scanning**: Scan documents directly from your scanner with a simple button click
- **Smart Filename Suggestions**: AI-powered filename recommendations based on document content using OpenAI's GPT-4o-mini
- **Direct Paperless Integration**: Upload scanned documents directly to Paperless-ngx with proper metadata
- **Modern GUI**: Clean, intuitive interface built with tkinter
- **Scanner Detection**: Automatic detection and management of available scanners
- **Configurable**: Easy configuration through YAML files
- **Cross-Platform**: Works on Windows (with scanner support via WIA)

## Screenshots

*[Screenshots would go here]*

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows OS (for scanner support)
- A scanner connected to your computer
- Paperless-ngx instance running
- OpenAI API key (optional, for smart filename suggestions)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd scanner
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the application**:
   Create a `config.yaml` file in the project directory:
   ```yaml
   api_url: "https://your-paperless-instance.com"
   api_token: "your-paperless-api-token"
   openai_api_key: "your-openai-api-key"  # Optional
   ```

4. **Get your Paperless API token**:
   - Log into your Paperless-ngx instance
   - Go to Settings → Users → Your User → API Tokens
   - Create a new token with appropriate permissions

## Usage

### Basic Workflow

1. **Launch the application**:
   ```bash
   python app.py
   ```

2. **Select your scanner** (if multiple are available)

3. **Click "Scan Document"** to scan your document

4. **Enter a filename** or use the AI-suggested filename

5. **Click "Save"** to save the document locally

6. **Click "Upload to Paperless"** to upload to your Paperless-ngx instance

### AI-Powered Filename Suggestions

The application can automatically suggest filenames based on the document content:

- After scanning, the AI will analyze the document and suggest a descriptive filename
- You can accept the suggestion or enter your own filename
- Filenames are automatically cleaned (spaces replaced with underscores, invalid characters removed)

### Configuration Options

#### Paperless-ngx Configuration
- `api_url`: Your Paperless-ngx instance URL
- `api_token`: Your Paperless API token

#### OpenAI Configuration (Optional)
- `openai_api_key`: Your OpenAI API key for smart filename suggestions

## File Structure

```
scanner/
├── app.py              # Main GUI application
├── scanner.py          # Scanner and Paperless integration
├── ai.py              # AI-powered filename suggestions
├── config.yaml        # Configuration file
├── requirements.txt   # Python dependencies
├── README.md         # This file
└── License.md        # License information
```

## API Integration

### Paperless-ngx API
The application integrates with Paperless-ngx using its REST API:
- Uploads documents with proper metadata
- Uses the filename as the document title
- Supports various image formats (JPEG, PNG, BMP, TIFF)

### OpenAI API (Optional)
For smart filename suggestions:
- Uses GPT-4o-mini for document analysis
- Analyzes visual content to suggest descriptive filenames
- Configurable parameters for response length and creativity

## Troubleshooting

### Common Issues

**Scanner not detected**:
- Ensure your scanner is connected and powered on
- Check that WIA drivers are properly installed
- Try refreshing the scanner list

**Upload fails**:
- Verify your Paperless-ngx URL and API token
- Check that your Paperless instance is accessible
- Ensure the API token has proper permissions

**AI suggestions not working**:
- Verify your OpenAI API key is correct
- Check your internet connection
- Ensure you have sufficient OpenAI API credits

### Debug Mode

Run with debug output:
```bash
python app.py --debug
```

## Development

### Adding New Features

1. **Scanner Support**: The scanner module uses Windows WIA for scanner communication
2. **AI Integration**: The AI module can be extended to support other AI providers
3. **GUI**: Built with tkinter for cross-platform compatibility

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Released under GPL v3. See [License.md](License.md) for details.

## Acknowledgments

- Paperless-ngx team for the excellent document management system
- OpenAI for providing the AI capabilities
- Python community for the excellent libraries used in this project