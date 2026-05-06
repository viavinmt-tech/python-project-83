PORT ?= 8000

install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
	uv run ruff check page_analyzer/
	uv run ruff format --check page_analyzer/

lint-fix:
	uv run ruff check --fix page_analyzer/
	uv run ruff format page_analyzer/