# WebQuills: Web Publishing for Everyone

The goal of the WebQuills project is to produce and maintain a web publishing system that anyone can use.

- WCAG 2.2 AA conformant publishing tools
- Lightweight and self-hostable.
- Requires no coding skills
- Provides numerous site templates
- Produces static HTML sites that:
    * conform to WCAG 2.2 Level AA
    * have Green Lighthouse scores across the board
    * are internationalized and ready for translation


## Project Status

Bootstrapping, not usable yet.

## Getting Started

After checking out the code, you will need to configure the WebQuills environment. Copy
the `example.env` file to `.env` and edit. You will need to set at least two variables:

* `WEBQUILLS_ROOT_DOMAIN` must be set to your domain. For local development, you can use a fake domain like "example.com".
* `SECRET_KEY` should be set to a random string. You can generate one using the following command.

```sh
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Adjust any other variables in your `.env` file as desired for your installation, including the locations of your database and redis servers (if used).

To setup your database, run the following commands:

```sh
python ./manage.py migrate
python ./manage.py createsuperuser  # Interactive
python ./manage.py create_site
```

The standard Django `createsuperuser` command will prompt you for user information and
create the first user. The `create_site` command will create your first site (the site
that will serve the CMS). By default, this first will be `www.WEBQUILLS_ROOT_DOMAIN`
and will be aliased to the `localhost` domain for convenience of development and
testing. If you don't want the defaults, run the command with the `--help` flag to
see your options.
