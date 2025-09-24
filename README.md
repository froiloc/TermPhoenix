# TermPhoenix 🔥

*An intelligent web crawler that extracts special-interest terminology from websites*

TermPhoenix rises from the ashes of unstructured web content to uncover the hidden terminology that defines special interests, fandoms, and niche communities. Like a phoenix, it rebirths raw text into organized, scored term lists.

## 🚀 Features

- **Smart Crawling**: Configurable depth, rate limiting, and domain control
- **Advanced Scoring**: Emphasis detection, capitalization weighting, cross-page significance
- **N-gram Detection**: Multi-word phrase extraction with intelligent stop-word handling
- **Quantile Normalization**: 0-100 scoring with outlier management
- **SQLite Cache**: Resume interrupted crawls and re-analyze with different parameters

## 📋 Planned Parameters

### Crawling Behavior
- `--url`: Starting URL(s)
- `--depth`: Crawl depth (0 = single page)
- `--allow-leave-domain`: Permit cross-domain crawling
- `--ignore-robots-txt`: Bypass robots.txt restrictions
- `--threads`: Parallel request count (0-16)
- `--scan-behavior`: Rate limiting profile (0-5)

### Analysis Parameters
- `--threshold-word`: Minimum score for single words (0-100)
- `--threshold-n-grams`: Minimum score for phrases (0-100)
- `--language`: Primary language (de/en)
- `--update-cache`: Force recrawl ignoring cache

### Output Control
- `--output-format`: JSON, CSV, Excel
- `--min-frequency`: Absolute frequency cutoff
- `--include-common-words`: Keep stop words in results

## 🗺️ Development Roadmap

### Version 0.1 "Phoenix Egg" (MVP) - 40-60 hours
- Basic crawling with SQLite cache
- HTML parsing and text extraction
- Simple tokenization with attribute collection

### Version 0.2 "Hatchling" - 30-50 hours  
- Word frequency counting and emphasis scoring
- Capitalization detection and basic filtering
- Quantile normalization system

### Version 0.3 "Fledgling" - 40-60 hours
- N-gram generation and pattern detection
- Rare term rescue algorithm
- Cross-page significance analysis

### Version 0.4 "Young Phoenix" - 50-70 hours
- Boilerplate detection and removal
- Memory optimization and performance tuning
- Validation and quality measurement

### Version 0.5 "Mature Phoenix" - 40-60 hours
- Configuration file support
- Excel export with statistics
- Usability improvements

### Version 1.0 "Firebird" - 60-80 hours
- Production readiness and comprehensive testing
- Documentation and example projects
- Final optimization and bug fixes

**Total Estimated Development: 260-380 hours**

Starting: 2025-09-23

## 🛠️ Technology Stack

- **Python 3.12** - Core programming language
- **BeautifulSoup4** - HTML parsing
- **SQLite** - Caching and data storage
- **NLTK** - Stop words and basic NLP
- **pandas** - Data analysis and Excel export
- **requests** - HTTP handling

## 🤝 Contributing

This project is developed through an innovative human-AI collaboration between a passionate developer and Phoenix, an AI assistant specializing in code architecture and problem-solving.

## 📄 License

GPL 3.0 License - see LICENSE file for details

---

*"Like a phoenix, we rise from complexity to clarity, one term at a time."*
