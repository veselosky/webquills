# WebQuills: A Django Publishing System

Webquills is an example of how to construct a publishing system with Django,
using development best practices.

- Configuration from environment variables using django-environ
- Unit testing with pytest
- Testing matrix against multiple Python and Django versions using tox
- Tests include checks for missing migrations and code style (code formatted
  with Black)
- Continuous integration testing using Github Actions workflows
- Python dependencies managed with pip-tools for consistent repeatable builds
  (transitive dependencies are locked)
- Tedious functions automated with the `run` script

Key architectural features of the software include:

- Multi-tenant using a custom Sites framework compatible with Django's Sites
  framework
- Themes installable as Django apps (theming is still a work in progress)
