# chat-bot
# Project Setup Guide

## Overview

This document provides a step-by-step guide to setting up and running the project. It includes details about API dependencies, installation requirements, and additional instructions for Linux users.

## API Requirements

The project depends on the following APIs:

1. **GROQ API**

   - [GROQ API Documentation](<https://console.groq.com/docs/overview>)
   - Ensure you have access to the API and obtain the required API keys for authentication.

2. **Langchain API**

   - [Langchain API Documentation](<https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key>)
   - Used for integrating advanced language model capabilities within the application.

## Installation Instructions

### Prerequisites

- **Python Version**: 3.10 (Ensure you have Python 3.10 installed on your system)
- **pip**: Python package manager (comes pre-installed with Python 3.10)
- **Createa .env file**: 
            Variables: - GROQ_API_KEY
                       - LANGCHAIN_API_KEY


### Installation Steps

1. Clone the repository:

   ```sh
   git clone <repository-url>
   git checkout backend
   cd <project-directory>
   ```

2. Install required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

### Special Instructions for Linux Users

- The package **pywin32** (Windows-specific) is not required on Linux-based systems.
- Before running the installation command, remove `pywin32` from the `requirements.txt` file:
  ```sh
  sed -i '/pywin32/d' requirements.txt
  ```
  Alternatively, you can manually edit `requirements.txt` and delete the line containing `pywin32`.

## Running the Project

After installing dependencies, you can start the application using:

```sh
cd backend
python app.py
```

Ensure that you have properly configured the API keys and environment variables as needed for the APIs used in the project.

