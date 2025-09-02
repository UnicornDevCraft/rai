# Template matching API
This project is the backend part of the RAI interview task.

## Getting started
### Install system dependencies
This project uses python 3.12 with `uv`. You can use `pyenv` to manage python versions: https://github.com/pyenv/pyenv.
To install uv, please follow the guide at https://docs.astral.sh/uv/getting-started/installation/.

### Install project dependencies
In the project root, run
```shell
uv sync --all-extras
```

### DB and storage setup
In the project root, run
```shell
mkdir storage
cd template_matching_api/scripts
uv run --frozen python create_and_seed_db.py
cp -R storage_seed/ ../../storage/
```

### Starting the API
in the project root, run
```shell
uv run --frozen fastapi dev template_matching_api/main.py
```
The API should then be available at http://127.0.0.1:8000, the OpenAPI documentation is available at http://127.0.0.1:8000/docs.
You can test the API by navigating to http://127.0.0.1:8000/api/document-template/

### Testing
You can run tests using `pytest`
```shell
uv run --frozen pytest template_matching_api/tests
```

### MyPy
You can check types using `mypy`
```shell
uv run --frozen mypy . --install-types --non-interactive
```
