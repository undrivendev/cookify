This is a python script which transforms a project in a
[cookiecutter](https://www.cookiecutter.io/) template by substituting the contents in
files and file paths with cookiecutter placeholders.

The name and value of placeholders will depend on the CLI arguments passed to the
script.

I've used this only for .NET projects, but other project types should also work with
minor tweaking.

## Like it? Give a star! :star:

If you like this project, you learned something from it, or you are using it in your
applications, please press the star button. Thanks!

## Motivation

I needed a way to transform projects written in different programming languages to
cookiecutter templates in order to simplify project bootstrapping.

Those projects do not follow the cookiecutter template folder structure out of the box,
so I needed a way to do it on the fly.

## Usage

Prerequisites: [poetry](https://python-poetry.org/)

Change directory into the project one and just execute `poetry run python main.py` file
with these command-line arguments:

1. The folder containing the project to convert
2. The first placeholder name
3. The first placeholder value
4. The second placeholder name
5. The second placeholder value

Note: only two placeholders are supported for the time being.

Example:

```
poetry run python main.py /work/_temp/WebApiTemplate solution_name WebApiTemplate sample_entity_name Customer
```

## Examples

I use this to generate a cookiecutter template for
[my other project](https://github.com/undrivendev/cookify). Here's the result:
[WebApiTemplate](https://github.com/undrivendev/template-webapi-aspnet/tree/cookiecutter).
