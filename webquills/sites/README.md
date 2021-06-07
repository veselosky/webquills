# Webquills Sites Framework

The Django sites framework is not particularly well geared for serving multiple
sites from the same server process. Webquills sites framework improves on the
Django sites framework in the following ways.

1. An enhanced Site model adding Webquills functionality, acting as a container for a site's configuration and content.
2. An alternate sites middleware that:
   1. Loads the Webquills Site model and related objects efficiently
   2. Selects the site based on the domain, falling back to SITE_ID if no match
3. Allows you to serve multiple sites from the same Django process pool
