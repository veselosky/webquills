# WebQuills: A Django Publishing System

Webquills is an example of how to construct a publishing system with Django. Key architectural features include:

- Configuration from environment variables using django-environ
- Unit testing with pytest
- Testing against multiple Python and Django versions using tox
- Tests include checks for missing migrations and code style
- Multi-tenant using a custom Sites framework compatible with Django's Sites framework
- Themes installable as Django apps (theming is still a work in progress)
- Tedious functions automated with the `run` script

## Notes on Images: upload, resizing, cropping, etc

Wagtail images had some nice features, but is tightly tied to Wagtail.

- django-responsive-images has resize-on-render tags and basic feature set using pillow.
- django-daguerre has smart resizing with "areas", nice widgets, but uses a view to resize on DL.
- Both of the above store everything in the DB, not just the FS. Not a deal-breaker.
- sorl-thumbnail is the old-school, maintained by Jazzband, but lacking newer features.
