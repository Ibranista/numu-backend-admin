# NUMU Backend Admin

This project is a Django backend with real-time capabilities using Django Channels and WebSocket connections.

## Features

- **Django Channels** for WebSocket support for real-time communication
- **Redis/Memurai** as the channel layer backend (for windows use memurai or use WSL)

## Installation & Environment Preparation

1. **Activate Evnironment**
2. **Install Python 3** (used python 3.13.3 for this project)
3. **Install pipenv** for environment and dependency management:

   ```
   source env/bin/activate
   or
   source env/Scripts/activate
   ```

   pip shell
   pip install pipenv

````

4. **Install dependencies and activate the environment:**

   ```bash
   pipenv install
   pipenv shell
````

## Running the Server

- **For local development (accessible on localhost):**

  ```bash
  pipenv run daphne -p 8000 backend.asgi:application
  ```

- **For network access (e.g., from an emulator or other devices):**

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
