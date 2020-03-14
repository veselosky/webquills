# WebQuills Isolation

> Development Status :: 3 - Alpha Framework :: Django :: 3.0 Framework ::
> Wagtail :: 2 Programming Language :: Python :: 3.6 Programming Language ::
> Python :: 3.7 Programming Language :: Python :: 3.8

WARNING: This code should be considered experimental. It has not been throughly
tested in the context of real Wagtail installations. It probably has lots of
leaks. Do not rely on it to preserve isolation of confidential information
without performing your own testing.

The goal of the Isolation app is to provide tenant isolation in the Wagtail
Admin so that you can run a multi-tenant installation without tenants seeing
each other's content or other models, effectively without knowing that other
tenants exist.

Requirements for tenant isolation include:

- A Wagtail user would be assigned to exactly ONE "tenant"
- A Wagtail user could create and have access to one or multiple sites within
  the tenant
- Only Pages for the tenant's sites would be visible in the Page Explorer
- Only Collections belonging to the tenant would be visible in Images, Documents
- Only Snippets belonging to the tenant would be visible in Snippet views
- Only SiteSettings for the tenant's sites would be visible in SiteSettings

In a perfect world, it would also be possible to create Collections or Page
trees that were shareable across sites and tenants, but that's not a requirement
for this version.

## The Approach

The approach we have taken to implement the above requirements consists of a few
changes, working as much as possible within the existing Wagtail framework.

1. Make the Wagtail Admin honor the Django Admin's "view" permission.
2. Create a Group to represent each tenant.
3. Create a node in the Page tree to act as that tenant's root node.
4. Create a node in the Collection tree to act as that tenant's root node.
5. Implement isolated Snippets as Wagtail CollectionItems.
6. Assign appropriate group permissions to ensure isolation.

Wagtail already partially implements view permissions, applying only to Snippet
models. You can easily suppress access to Snippet models simply by unticking the
"view" box on the group admin page. In fact, Snippet permissions are not granted
by default and must be explicitly added to grant access.

The **page chooser** can be made to honor view permissions using the
`construct_page_chooser_queryset` [hook][1].

The **document chooser** can be made to honor view permissions using the
`construct_document_chooser_queryset` [hook][2].

The **image chooser** can be made to honor view permissions using the
`construct_image_chooser_queryset` [hook][3].

The **page explorer** can be made to honor view permissions using the
`construct_explorer_page_queryset` [hook][4].

The **collection chooser** cannot be customized in this way as there is no hook
to customize the collection queryset. To filter collections, you would need to
override the template that renders the chooser,
`wagtailadmin/shared/collection_chooser.html`, and insert a template tag that
provides the filtered queryset, as suggested in [this Github comment][5].

## Issues and limitations with this approach

- Although Collections are implemented as a Tree, they are presented in the
  Wagtail Admin as a flat list. There is currently no way to select a parent
  when creating a Collection. This makes management tricky. See [issue 3380][6].
- With this scheme, Collections are scoped to the tenant, and not to a specific
  site. To isolate at the site level, you would need to adopt a strict one site
  per tenant policy.
- User and Group administration within a tenant is not addressed. Those models
  remain "global" for now. A user with Admin-level access is NOT scoped to a
  tenant.

[1]:
  https://docs.wagtail.io/en/v2.8/reference/hooks.html#construct-page-chooser-queryset
[2]:
  https://docs.wagtail.io/en/v2.8/reference/hooks.html#construct-document-chooser-queryset
[3]:
  https://docs.wagtail.io/en/v2.8/reference/hooks.html#construct-image-chooser-queryset
[4]:
  https://docs.wagtail.io/en/v2.8/reference/hooks.html#construct-explorer-page-queryset
[5]: https://github.com/wagtail/wagtail/issues/4488#issuecomment-494128414
[6]: https://github.com/wagtail/wagtail/issues/3380
