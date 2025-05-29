# code-generator

[**code-generator**](https://code-generator-uyif.onrender.com) is an application that generates functional code projects from natural language descriptions (and optionally images), using advanced language models (OpenAI GPT-4.1-nano). The system consists of a backend (FastAPI) and a frontend (Streamlit), allowing you to download the generated project, explore its structure, and visualize the files.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Agent Flow](#agent-flow)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Deployment with Docker](#deployment-with-docker)
- [Notes and Next Steps](#notes-and-next-steps)

---

## Features

- Automatic generation of code projects from natural language descriptions.
- Optional support for images as additional context.
- Security validation of the prompt before code generation.
- Iterative process for code generation and validation.
- Automatic linter (Ruff) to ensure code quality.
- Download the project as a ZIP file.
- Integrated file explorer in the frontend.
- Modern and minimalist user interface (Streamlit).

---

## Architecture

- **Backend:** FastAPI, responsible for orchestrating code generation, validation, and storage.
- **Frontend:** Streamlit, allows users to describe the application, upload images, explore, and download the generated project.
- **LLM Model:** OpenAI GPT-4.1-nano (configurable), used for code generation and validation.
- **Containers:** Full support for Docker and docker-compose.

---

## Agent Flow

The core of the application is an **agent** that follows a structured flow to ensure the security and quality of the generated code. The flow is implemented as a state graph using [langgraph](https://github.com/langchain-ai/langgraph).

### Flow Diagram

```
[Security]  
   |--(peligroso)--> [Finisher]
   |--(seguro)------> [Generator1] -> [Generator2] -> [Generator3] 
                                        \|/
                                         v
                                   [Aggregator]
                                         |
                                         v
                                    [Validator]
                                   /           \
                        (OK o max iter)      (NO OK)
                          |                     |
                      [Saver]                [Aggregator]
                          |
                      [Linter]
                       /    \
                   (OK)    (NO OK)
                    |         |
               [Finisher]  [Aggregator]
```

### Explanation of Main Nodes

1. **Security:**  
   Evaluates whether the user's request is safe. If a dangerous prompt is detected, the flow ends and no code is generated.

2. **Generator1, Generator2, Generator3:**  
   Three code variants are generated from the user's description to encourage diversity and robustness.

3. **Aggregator:**  
   Takes the three variants and combines them into a final proposal, integrating feedback if available.

4. **Validator:**  
   Validates the generated code. If satisfactory ("OK") or the maximum number of iterations is reached, the flow proceeds; otherwise, it returns to the aggregator to refine the code.

5. **Saver:**  
   Saves the generated code in the corresponding file structure.

6. **Linter:**  
   Runs Ruff to ensure code quality. If there are errors, feedback is incorporated and the flow returns to the aggregator.

7. **Finisher:**  
   Saves the agent's history and compresses the project into a ZIP file for download.

This flow ensures that the generated code is safe, functional, and high-quality, allowing for automatic iterations until a satisfactory result is achieved.

---

## Installation

### Requirements

- Python 3.12
- Docker
- An OpenAI API key

### Clone the repository

```bash
git clone https://github.com/Yamilhb/code-generator.git
cd code-generator
```

### Installation with Docker

```bash
docker-compose up --build
```

This will start both the backend (FastAPI) and the frontend (Streamlit).

---

## Usage

1. Access the frontend at [http://localhost:8501](http://localhost:8501).
2. Describe the application you want to generate.
3. (Optional) Upload an image to provide more context.
4. Enter your OpenAI API key.
5. Click **RUN!** and wait for the code to be generated.
6. Explore the generated files and download the project as a ZIP.

---

## Environment Variables

They are defined in `docker-compose.yml`. Here you can specify the model you want to use.

---

## Local Deployment

The project includes `Dockerfile` and `docker-compose.yml` files to facilitate deployment:

```bash
docker-compose up --build
```

- The backend will be available at `http://localhost:8000`
- The frontend will be available at `http://localhost:8501`

---

## Notes and Next Steps

- [ ] Include support for PDF as input.
- [ ] Improve the frontend (more professional design).
- [ ] Allow iterative conversation with the user.
- [ ] Improve handling of large images.
- [ ] Possibility to select AI models from other providers.

---

**Thank you for using code-generator!**

---