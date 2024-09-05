## Clue-Less

A minimal version of the Clue game.

## Development Workflow

- Open pull requests against the main branch.
- Pull requests require at least one approving review to merge
- Development work should be done in feature branches.
- We will use the squash and merge strategy to merge pull requests into the main branch.
- Both the reviewer and the author are responsible for testing and ensuring that all PRs are functional before being merged.
- Follow best development practices for commit messages, creating tests, etc.

## Setup Instructions

1. Install python@3.12. You can install using [homebrew](https://brew.sh/) on MacOS, or directly from the [website](https://www.python.org/downloads/release/python-3120/).
For homebrew, you can use:
`brew install python@3.12`

2. Install pipx and poetry. [Poetry's documentation](https://python-poetry.org/docs/basic-usage/) suggests `pipx`, but you're welcome to use any installer to install `poetry`. Pipx installation instructions can be found [here](https://pipx.pypa.io/stable/installation/).
If using homebrew, you can use `brew install pipx` and `pipx install poetry` to install the two dependencies.

3. Once you have poetry and python installed, Clone this repository locally. While in the directory for your clone of the github repo, initialize the project using `poetry install`

## Running the Django App

Run the application using `poetry run python manage.py runserver`. The application will be served on `http://127.0.0.1:8000/` in your browser.

