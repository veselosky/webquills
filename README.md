# Webquills - By writers, for writers

To get started with development checkout the code and run:

```bash
python3.10 ./manage.py devsetup
```

Note that Python 3.10 or newer is required.

## Dependency Management

This project includes [pip-tools](https://pypi.org/project/pip-tools/) for dependency
management. There are two requirements files: `requirements.in` provides the acceptable
ranges of packages to install in a production environment (or any other environment);
`requirements-dev.in` provides packages to install in development environments. Both of
these have corresponding "pin" files: `requirements.txt` and `requirements-dev.txt`.

To add a new dependency, add it to the correct `.in` file, and then run
`manage.py pipsync` to regenerate the pin files and synchronize your current virtual
environment with the new pin files.

Any arguments passed to `manage.py pipsync` will be passed through to the underlying
`pip-compile` command. For example, to bump to the latest Django patch release use
`manage.py pipsync --upgrade-package django`. See the
[pip-tools docs](https://pypi.org/project/pip-tools/) for complete details.
