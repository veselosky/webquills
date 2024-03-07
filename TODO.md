# WebQuills Overhaul Task List

- [x] Consolidate requirements and manage with UV
- [x] Use UV to manage dev virtualenvs
- [ ] Update Github actions to include packaging releases
- [ ] Replace sites framework with Django, as in GenericSite
- [ ] Recreate the core content functions in a new app
- [ ] Scrap BS4 templates and reimplement templates framework-free
- [ ] Separate the views (and if necessary models) that support static generation, from
      those that are dynamic.
- [ ] Implement a static generation system that can build pages in the background using
      celery.
- [ ] Add compressor support for minifying JS and CSS.
- [ ] Store static assets gzipped to save resources.

## Models

- [ ] Merge original WebQuills models and GenericSite models with the intent to support
      multi-user blogs, including author profiles.
- [ ] Preserve the Author as separate model from WebQuills. Include profile info (bio,
      contact, socials) as well as default copyright attribution (can always be
      overriden at the object level).
- [ ] Keep Open Graph and add Schema.org outputs, but remove Pydantic dependency; just
      write output routines in the models directly.
