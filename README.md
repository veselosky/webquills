# WebQuills.com

This is the code that runs (or one day will run) webquills.com.

## Images: upload, resizing, cropping, etc

Wagtail images had some nice features, but is tightly tied to Wagtail.

- django-responsive-images has resize-on-render tags and basic feature set using pillow.
- django-daguerre has smart resizing with "areas", nice widgets, but uses a view to resize on DL.
- Both of the above store everything in the DB, not just the FS. Not a deal-breaker.
- sorl-thumbnail is the old-school, maintained by Jazzband, but lacking newer features.
