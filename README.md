## Clue-Less

A minimal version of the Clue game.

## Project Structure

The project is organized with a django application in the `cluegonauts` directory. The top-level directory only contains environment setup files and the README for the repository. The main directory structure is shown in the tree below:

```
.
├── cluegonauts
│   ├── app/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── clueless/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── templates
│   │   ├── consumers.py
│   │   ├── views.py
│   │   ├── routing.py
│   │   └── urls.py
│   ├── static/
│   ├── manage.py
├── .gitignore
├── pyproject.toml
├── poetry.lock
└── README.md
```

In this structure, the `app` directory contains the setup for the django application, such as [`settings.py`](/cluegonauts/app/see
), where application settings are defined, and [`urls.py`](/cluegonauts/app/urls.py), where urls for the application need to be configured. The `clueless` directory contains the main Django project files for the Clue game. HTML templates should be defined in the [`templates`](/cluegonauts/clueless/templates/) directory using the jinja2 templating syntax, and new views should be declared in [`urls.py`](/cluegonauts/clueless/urls.py) as well as [`views.py`](/cluegonauts/clueless/views.py). 

Consumers should be declared for any client-server messaging needs in [`consumers.py`](/cluegonauts/clueless/consumers.py) with corresponding websocket patterns declared in [`routing.py`](/cluegonauts/clueless/routing.py).

Any images, compiled css, compiled javascript, or other static files should be in the [`cluegonauts/static/clueless`](/cluegonauts/static/clueless/) directory with the appropriate directory for `css/` `images/` or `js/`. Any static CSS files should be minified to optimize performance.

## Development Workflow

- Open pull requests against the main branch. NEVER push new features to the main branch without a review.
- Pull requests require at least one approving review to merge.
- Development work should be done in feature branches.
- We will use the squash and merge strategy to merge pull requests into the main branch.
- Both the reviewer and the author are responsible for testing and ensuring that all PRs are functional before being merged.
- Follow best development practices for commit messages, creating tests, etc.
- Do not check in unnecessary files or secrets into the repository.
- Review the documentation under [References](#references) for more information.

## Setup Instructions

1. Install python@3.12. You can install using [homebrew](https://brew.sh/) on MacOS, or directly from the [website](https://www.python.org/downloads/release/python-3120/).
For homebrew, you can use:
`brew install python@3.12`

2. Install pipx and poetry. [Poetry's documentation](https://python-poetry.org/docs/basic-usage/) suggests `pipx`, but you're welcome to use any installer to install `poetry`. Pipx installation instructions can be found [here](https://pipx.pypa.io/stable/installation/).
If using homebrew, you can use `brew install pipx` and `pipx install poetry` to install the two dependencies.
    - When installing with pipx, you may see a warning saying poetry has not been added to PATH when you finish installation. pipx will prompt you to run `pipx ensurepath poetry` to add it to PATH, make sure you do this so you can run poetry commands.

3. Once you have poetry and python installed, Clone this repository locally. While in the directory for your clone of the github repo, initialize the project using `poetry install`

## Running the Django App

Run the application using `poetry run python manage.py runserver`. The application will be served on `http://127.0.0.1:8000/clueless` in your browser.

> Note: You may see a warning saying that you have unapplied migrations. This is not necessary as it just sets up the underlying database which we will not be using, and this warning can be safely ignored.


## References

Some documentation that may be useful in project development:
- [Django Documentation](https://docs.djangoproject.com/en/5.1/)
- [Github Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow)
- [Bootstrap Reference](https://getbootstrap.com/docs/5.0/getting-started/introduction/) - we'll be using the base bootstrap components for styling in this project. Use this website to browse the available CSS components.
