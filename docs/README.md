# Documentation Index

Welcome to the Discord T-Shirt Bot documentation! This index will help you find what you need.

## 📚 Getting Started

New to the project? Start here:

1. **[Setup Guide](SETUP.md)** - Installation and configuration
2. **[Quick Start](../README.md#quick-start)** - Get the bot running in minutes

## 🏗️ Architecture & Design

Understanding how the bot works:

- **[Architecture Documentation](ARCHITECTURE.md)** - System design and components
- **[API Reference](API_REFERENCE.md)** - Complete API documentation for all services

## 🚀 Deployment

Deploying to production:

- **[Deployment Guide](DEPLOYMENT.md)** - Google Cloud Run deployment (recommended)
- **[GitHub Actions Guide](GITHUB_ACTIONS.md)** - CI/CD pipeline setup

## 🧪 Testing

Writing and running tests:

- **[Testing Guide](TESTING.md)** - Comprehensive testing documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute and test your changes

## 📖 Documentation by Role

### For Users

Want to use the bot in your Discord server?

1. [Setup Guide](SETUP.md) - Install and configure
2. [Troubleshooting](SETUP.md#troubleshooting) - Common issues

### For Developers

Want to modify or contribute to the bot?

1. [Architecture](ARCHITECTURE.md) - Understand the codebase
2. [API Reference](API_REFERENCE.md) - Service documentation
3. [Testing Guide](TESTING.md) - Write and run tests
4. [Contributing Guide](CONTRIBUTING.md) - Contribution workflow

### For DevOps/Deployers

Want to deploy and maintain the bot?

1. [Deployment Guide](DEPLOYMENT.md) - Cloud Run deployment
2. [GitHub Actions Guide](GITHUB_ACTIONS.md) - CI/CD setup
3. [Architecture](ARCHITECTURE.md#deployment-architecture) - Deployment architecture

## 🔍 Quick Reference

### Common Tasks

| Task | Documentation |
|------|---------------|
| Install locally | [Setup Guide](SETUP.md#installation) |
| Get API keys | [Setup Guide](SETUP.md#getting-api-keys) |
| Run the bot | [Setup Guide](SETUP.md#running-the-bot) |
| View design history | [Design Tracking](DESIGN_TRACKING.md) |
| Deploy to Cloud | [Deployment Guide](DEPLOYMENT.md) |
| Run tests | [Testing Guide](TESTING.md#running-tests) |
| Add new feature | [Contributing Guide](CONTRIBUTING.md) |
| Debug issues | [Setup Guide](SETUP.md#troubleshooting) |
| Set up CI/CD | [GitHub Actions Guide](GITHUB_ACTIONS.md) |

### Service Documentation

| Service | Purpose | Documentation |
|---------|---------|---------------|
| Discord Bot | Message monitoring | [API Reference](API_REFERENCE.md#tshirtbot) |
| LLM Parser | Message parsing | [API Reference](API_REFERENCE.md#llmparser) |
| Design Generator | Image creation | [API Reference](API_REFERENCE.md#designgenerator) |
| Printful Client | Product creation | [API Reference](API_REFERENCE.md#printfulclient) |
| Orchestrator | Workflow coordination | [API Reference](API_REFERENCE.md#tshirtorchestrator) |

## 📝 Documentation Structure

```
docs/
├── README.md              # This file - documentation index
├── SETUP.md              # Installation and setup guide
├── DEPLOYMENT.md         # Deployment to Google Cloud Run
├── ARCHITECTURE.md       # System architecture and design
├── API_REFERENCE.md      # Complete API documentation
├── DESIGN_TRACKING.md    # Design history and tracking
├── TESTING.md            # Testing guide and best practices
├── GITHUB_ACTIONS.md     # CI/CD pipeline documentation
└── CONTRIBUTING.md       # Contributing guidelines
```

## 🔗 External Resources

### APIs Used

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Printful API](https://developers.printful.com/docs/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)

### Tools & Frameworks

- [Python 3.11+](https://docs.python.org/3/)
- [UV Package Manager](https://github.com/astral-sh/uv)
- [pytest](https://docs.pytest.org/)
- [Docker](https://docs.docker.com/)
- [Google Cloud Run](https://cloud.google.com/run/docs)

## 🆘 Getting Help

Can't find what you need?

1. **Search** the documentation (Ctrl+F)
2. **Check** [troubleshooting guides](SETUP.md#troubleshooting)
3. **Review** [existing issues](https://github.com/yourusername/discord-tshirt-bot/issues)
4. **Ask** in [GitHub Discussions](https://github.com/yourusername/discord-tshirt-bot/discussions)
5. **Open** a [new issue](https://github.com/yourusername/discord-tshirt-bot/issues/new)

## 📊 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| Setup Guide | ✅ Complete | Latest |
| Deployment Guide | ✅ Complete | Latest |
| Architecture | ✅ Complete | Latest |
| API Reference | ✅ Complete | Latest |
| Testing Guide | ✅ Complete | Latest |
| GitHub Actions | ✅ Complete | Latest |
| Contributing | ✅ Complete | Latest |

## 🔄 Keeping Documentation Updated

When making changes to the code:

1. **Update relevant docs** - If behavior changes, update the docs
2. **Add new sections** - Document new features thoroughly
3. **Update examples** - Keep code examples working
4. **Check links** - Ensure all internal links work
5. **Test instructions** - Verify setup/deployment steps work

## 📚 Documentation Best Practices

This documentation follows these principles:

- ✅ **Clear and concise** - Easy to understand
- ✅ **Comprehensive** - Covers all aspects
- ✅ **Example-driven** - Includes working examples
- ✅ **Up-to-date** - Maintained with code changes
- ✅ **Well-organized** - Easy to navigate
- ✅ **Searchable** - Clear headings and keywords

## 🎯 Next Steps

**New User?**
→ Start with the [Setup Guide](SETUP.md)

**Want to Deploy?**
→ Read the [Deployment Guide](DEPLOYMENT.md)

**Want to Contribute?**
→ Check the [Contributing Guide](CONTRIBUTING.md)

**Want to Understand the Code?**
→ Review the [Architecture](ARCHITECTURE.md)

---

**Questions or suggestions about documentation?**
Open an issue with the `documentation` label!
