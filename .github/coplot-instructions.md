# Code Standards

## Internationalization and Localization (i18n and l10n)

All Django models must contain a Meta inner class declaring a `verbose_name` and `verbose_name_plural` marked for translation.

All Django fields must declare a `verbose_name` argument marked for translation.

If a field declaration contains a `help_text` argument, it must be marked for translation.

`ValidationError` messages must be marked for translation.

User-visible strings in Django templates must be marked for translation.

## Accessibility

All HTML files and Django templates must conform to WCAG 2.1 Level AA.
