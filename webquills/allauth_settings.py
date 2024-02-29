# (default: "allauth.account.adapter.DefaultAccountAdapter")
# Specifies the adapter class to use, allowing you to alter certain default behaviour.
# ACCOUNT_ADAPTER

# The default behaviour is to redirect authenticated users to LOGIN_REDIRECT_URL when
# they try accessing login/signup pages.
# By changing this setting to False, logged in users will not be redirected when they
# access login/signup pages.
# (default: True)
# ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS

# Specifies the login method to use – whether the user logs in by entering their
# username, email address, or either one of both. Setting this to "email" requires
# ACCOUNT_EMAIL_REQUIRED=True
# (default: "username", alternatives: "email" or "username_email")
ACCOUNT_AUTHENTICATION_METHOD = "email"

# When disabled (False), users can add one or more email addresses (up to a maximum of
# ACCOUNT_MAX_EMAIL_ADDRESSES) to their account and freely manage those email addresses.
# When enabled (True), users are limited to having exactly one email address that they
# can change by adding a temporary second email address that, when verified, replaces
# the current email address.
# (default: False)
# ACCOUNT_CHANGE_EMAIL = True

# Determines whether or not an email address is automatically confirmed by a GET request.
# GET is not designed to modify the server state, though it is commonly used for email
# confirmation. To avoid requiring user interaction, consider using POST via Javascript
# in your email confirmation template as an alternative to setting this to True.
# (default: False)
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

# The URL to redirect to after a successful email confirmation, in case no user is logged in.
# (default: settings.LOGIN_URL)
# ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL

# The URL to redirect to after a successful email confirmation, in case of an
# authenticated user. Set to None to use settings.LOGIN_REDIRECT_URL.
# (default: None)
# ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL

# Determines the expiration date of email confirmation mails (# of days).
# (default: 3)
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 8

# In order to verify an email address a key is mailed identifying the email address to
# be verified. In previous versions, a record was stored in the database for each
# ongoing email confirmation, keeping track of these keys. Current versions use HMAC
# based keys that do not require server side state.
# (default: True)
# ACCOUNT_EMAIL_CONFIRMATION_HMAC

# The user is required to hand over an email address when signing up.
# (default: False)
ACCOUNT_EMAIL_REQUIRED = True

# Determines the email verification method during signup – choose one of "mandatory",
# "optional", or "none".
# Setting this to "mandatory" requires ACCOUNT_EMAIL_REQUIRED to be True.
# When set to "mandatory" the user is blocked from logging in until the email address
# is verified. Choose "optional" or "none" to allow logins with an unverified email
# address. In case of "optional", the email verification mail is still sent, whereas in
#  case of “none” no email verification mails are sent.
# (default: "optional")
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# Subject-line prefix to use for email messages sent. By default, the name of the
# current Site (django.contrib.sites) is used.
# (default: "[Site] ")
# ACCOUNT_EMAIL_SUBJECT_PREFIX

# Configures whether password reset attempts for email addresses which do not have an
# account result in sending an email.
# (default: True)
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False

# The default protocol used for when generating URLs, e.g. for the password forgotten
# procedure. Note that this is a default only – see the section on HTTPS for more
# information.
# (default: "http")
# ACCOUNT_DEFAULT_HTTP_PROTOCOL

# Users can request email confirmation mails via the email management view, and,
# implicitly, when logging in with an unverified account. In order to prevent users
# from sending too many of these mails, a rate limit is in place that allows for one
# confirmation mail to be sent per the specified cooldown period (in seconds).
# (default: 180)
# ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN

# Maximum length of the email field. You won’t need to alter this unless using MySQL
# with the InnoDB storage engine and the utf8mb4 charset, and only in versions lower
# than 5.7.7, because the default InnoDB settings don’t allow indexes bigger than 767
# bytes. When using utf8mb4, characters are 4-bytes wide, so at maximum column indexes
# can be 191 characters long (767/4). Unfortunately Django doesn’t allow specifying
# index lengths, so the solution is to reduce the length in characters of indexed text
# fields. More information can be found at MySQL’s documentation on converting between
# 3-byte and 4-byte Unicode character sets.
# (default: 254)
# ACCOUNT_EMAIL_MAX_LENGTH

# The maximum amount of email addresses a user can associate to his account. It is safe
# to change this setting for an already running project – it will not negatively affect
# users that already exceed the allowed amount. Note that if you set the maximum to 1,
# users will not be able to change their email address unless you enable ACCOUNT_CHANGE_EMAIL.
# (default: None)
# ACCOUNT_MAX_EMAIL_ADDRESSES

# Used to override the builtin forms. Defaults to:
# ACCOUNT_FORMS = {
#     'add_email': 'allauth.account.forms.AddEmailForm',
#     'change_password': 'allauth.account.forms.ChangePasswordForm',
#     'login': 'allauth.account.forms.LoginForm',
#     'reset_password': 'allauth.account.forms.ResetPasswordForm',
#     'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
#     'set_password': 'allauth.account.forms.SetPasswordForm',
#     'signup': 'allauth.account.forms.SignupForm',
#     'user_token': 'allauth.account.forms.UserTokenForm',
# }

# Number of failed login attempts. When this number is exceeded, the user is prohibited
# from logging in for the specified ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT seconds. Set to None
# to disable this functionality. Important: while this protects the allauth login view,
# it does not protect Django’s admin login from being brute forced.
# (default: 5)
# ACCOUNT_LOGIN_ATTEMPTS_LIMIT

# Time period, in seconds, from last unsuccessful login attempt, during which the user
# is prohibited from trying to log in.
# (default: 300)
# ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT

# The default behaviour is not log users in and to redirect them to
# ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL.
# By changing this setting to True, users will automatically be logged in once they
# confirm their email address. Note however that this only works when confirming the
# email address immediately after signing up, assuming users didn’t close their browser
# or used some sort of private browsing mode.
# (default: False)
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Determines whether or not the user is automatically logged out by a GET request. GET
# is not designed to modify the server state, and in this case it can be dangerous. See
# LogoutView in the documentation for details.
# (default: False)
# ACCOUNT_LOGOUT_ON_GET

# Determines whether or not the user is automatically logged out after changing or
# setting their password. See documentation for Django’s session invalidation on
# password change.
# (default: False)
# ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE

# By changing this setting to True, users will automatically be logged in once they
# have reset their password. By default they are redirected to the password reset done page.
# (default: False)
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

# The URL (or URL name) to return to after the user logs out. Defaults to Django’s
# LOGOUT_REDIRECT_URL, unless that is empty, then "/" is used.
# (default: settings.LOGOUT_REDIRECT_URL or "/")
# ACCOUNT_LOGOUT_REDIRECT_URL

# render_value parameter as passed to PasswordInput fields.
# (default: False)
# ACCOUNT_PASSWORD_INPUT_RENDER_VALUE

# A string pointing to a custom token generator (e.g. ‘myapp.auth.CustomTokenGenerator’)
# for password resets. This class should implement the same methods as
# django.contrib.auth.tokens.PasswordResetTokenGenerator or subclass it.
# (default: "allauth.account.forms.EmailAwarePasswordResetTokenGenerator")
# ACCOUNT_PASSWORD_RESET_TOKEN_GENERATOR

# This setting determines whether the username is stored in lowercase (False) or
# whether its casing is to be preserved (True). Note that when casing is preserved,
# potentially expensive __iexact lookups are performed when filter on username. For
# now, the default is set to True to maintain backwards compatibility.
# (default: True)
# ACCOUNT_PRESERVE_USERNAME_CASING

# Controls whether or not information is revealed about whether or not a user account
# exists. For example, by entering random email addresses in the password reset form
# you can test whether or not those email addresses are associated with an account.
# Enabling this setting prevents that, and an email is always sent, regardless of
# whether or not the account exists. Note that there is a slight usability tax to pay
# because there is no immediate feedback.
# Whether or not enumeration can be prevented during signup depends on the email
# verification method. In case of mandatory verification, enumeration can be properly
# prevented because the case where an email address is already taken is indistinguishable
# from the case where it is not. However, in case of optional or disabled email
# verification, enumeration can only be prevented by allowing the signup to go through,
# resulting in multiple accounts sharing same email address (although only one of the
# accounts can ever have it verified). When enumeration is set to True, email address
# uniqueness takes precedence over enumeration prevention, and the issue of multiple
# accounts having the same email address will be avoided, thus leaking information.
# Set it to "strict" to allow for signups to go through.
# (default: True)
# ACCOUNT_PREVENT_ENUMERATION


# In order to be secure out of the box various rate limits are in place. The rate limit
# mechanism is backed by a Django cache. Hence, rate limiting will not work properly if
# you are using the DummyCache. To disable, set to {}. When rate limits are hit the
# 429.html template is rendered. Defaults to:
# ACCOUNT_RATE_LIMITS = {
#     # Change password view (for users already logged in)
#     "change_password": "5/m",
#     # Email management (e.g. add, remove, change primary)
#     "manage_email": "10/m",
#     # Request a password reset, global rate limit per IP
#     "reset_password": "20/m",
#     # Rate limit measured per individual email address
#     "reset_password_email": "5/m",
#     # Password reset (the view the password reset email links to).
#     "reset_password_from_key": "20/m",
#     # Signups.
#     "signup": "20/m",
#     # NOTE: Login is already protected via `ACCOUNT_LOGIN_ATTEMPTS_LIMIT`
# }

# Specifies whether or not reauthentication is required before the user can alter his account.
# (default: False)
# ACCOUNT_REAUTHENTICATION_REQUIRED

# Before asking the user to reauthenticate, we check if a successful (re)authentication
# happened within the amount of seconds specified here, and if that is the case, the
# new reauthentication flow is silently skipped.
# (default: 300)
# ACCOUNT_REAUTHENTICATION_TIMEOUT

# Controls the life time of the session. Set to None to ask the user (“Remember me?”),
# False to not remember, and True to always remember.
# (default: None)
# ACCOUNT_SESSION_REMEMBER

# When signing up, let the user type in their email address twice to avoid typo’s.
# (default: False)
# ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE

# A string pointing to a custom form class (e.g. 'myapp.forms.SignupForm') that is used
# during signup to ask the user for additional input (e.g. newsletter signup, birth
# date). This class should implement a def signup(self, request, user) method, where
# user represents the newly signed up user.
# (default: None)
# ACCOUNT_SIGNUP_FORM_CLASS

# When signing up, let the user type in their password twice to avoid typos.
# (default: True)
# ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE

# The URL (or URL name) to redirect to directly after signing up. Note that users are
# only redirected to this URL if the signup went through uninterruptedly, for example,
# without any side steps due to email verification. If your project requires the user
# to always pass through certain onboarding views after signup, you will have to keep
# track of state indicating whether or not the user successfully onboarded, and handle
# accordingly.
# (default: settings.LOGIN_REDIRECT_URL)
# ACCOUNT_SIGNUP_REDIRECT_URL

# A string defining the template extension to use, defaults to html.
# (default: "html")
# ACCOUNT_TEMPLATE_EXTENSION

# A list of usernames that can’t be used by user.
# (default: [])
ACCOUNT_USERNAME_BLACKLIST = ["admin", "administrator", "webquill", "webquills"]

# Enforce uniqueness of email addresses. On the database level, this implies that only
# one user account can have an email address marked as verified. Forms prevent a user
# from registering with or adding an additional email address if that email address is
# in use by another account.
# (default: True)
# ACCOUNT_UNIQUE_EMAIL

# A callable (or string of the form 'some.module.callable_name') that takes a user as
# its only argument and returns the display name of the user. The default implementation
# returns user.username.
# (default: a callable returning user.username)
# ACCOUNT_USER_DISPLAY

# The name of the field containing the email, if any. See custom user models.
# (default: "email")
# ACCOUNT_USER_MODEL_EMAIL_FIELD

# The name of the field containing the username, if any. See custom user models.
# (default: "username")
# ACCOUNT_USER_MODEL_USERNAME_FIELD

# An integer specifying the minimum allowed length of a username.
# (default: 1)
ACCOUNT_USERNAME_MIN_LENGTH = 2

# The user is required to enter a username when signing up. Note that the user will be
# asked to do so even if ACCOUNT_AUTHENTICATION_METHOD is set to email. Set to False
# when you do not wish to prompt the user to enter a username.
# (default: True)
# ACCOUNT_USERNAME_REQUIRED

# A path ('some.module.validators.custom_username_validators') to a list of custom
# username validators. If left unset, the validators setup within the user model
# username field are used.
# (default: None)
# ACCOUNT_USERNAME_VALIDATORS
