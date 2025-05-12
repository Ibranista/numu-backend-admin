# NUMU Backend Admin

NUMU Backend Admin is a Django backend with real-time capabilities using Django Channels and WebSocket connections. It supports scalable, interactive applications and is ready for both local and networked socket connections.

## Features

- ⚡ Real-time communication with Django Channels (WebSocket support)
- 🔗 Redis/Memurai as the channel layer backend (Memurai recommended for Windows)
- 🔒 Secure environment variable management for secrets (including Firebase)

## Getting Started

### 1. Clone the repository

```bash
git clone git@github.com:Ibranista/numu-backend-admin.git
```

### 2. Prepare your environment

- Install Python 3 (used: 3.13.3)
- Install pipenv for environment and dependency management:

```bash
pip install pipenv
```

- Activate your environment (choose the correct command for your OS):

```bash
source env/bin/activate
# or (Windows)
source env/Scripts/activate
```

- Enter pipenv shell:

```bash
pipenv shell
```

### 3. Install dependencies

```bash
pipenv install
```

### 4. Configure environment variables

- Ensure your `.env` file is set up with all required secrets and environment variables (see project docs for details).

### 5. Run the server

- For local development (localhost):

```bash
pipenv run daphne -p 8000 backend.asgi:application
```

- For network access (e.g., emulator or other devices):

```bash
pipenv run daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

## Channel Layer Backend

- The project uses **Redis** for the channel layer.
- On Windows, you can use **Memurai** as a Redis-compatible alternative: [https://www.memurai.com/](https://www.memurai.com/)
- Make sure Redis/Memurai is running before starting the server.

## Notes

- Ensure your `.env` file is set up with all required secrets and environment variables.
- For Firebase integration, credentials are loaded from environment variables for security.

---

**Happy developing with NUMU Backend Admin!**
