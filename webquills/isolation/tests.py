from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from wagtail.core.models import (
    Collection,
    GroupCollectionPermission,
    GroupPagePermission,
    Page,
)
from wagtail.images import get_image_model
from wagtail.documents import get_document_model

import webquills.isolation.wagtail_hooks as hooks


class TestPermittedCollectionFiltering(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Put scenario data in the DB"""
        # Add 2 groups
        cls.group1 = Group.objects.create(name="group1")
        cls.group2 = Group.objects.create(name="group2")
        # Add a user in one of the groups, and a superuser
        User = get_user_model()
        cls.user1 = User.objects.create(username="user1", password="a!@SDF")
        cls.user1.groups.set([cls.group1])
        cls.superuser = User.objects.create(
            username="superuser", password="a!@SDF", is_superuser=True
        )
        # For the multiple roots case, add a user in groups 1 & 2
        cls.user0 = User.objects.create(username="user0", password="a!@SDF")
        cls.user0.groups.set([cls.group1, cls.group2])

        # Add a root Page
        cls.rootPage = Page.add_root(title="Root Page", slug="root-page")
        # Add a sub-root Page for group1
        cls.page1 = cls.rootPage.add_child(title="Group 1 Root Page", slug="g1-root")
        cls.page3 = cls.page1.add_child(title="Another Group 1 Page", slug="g1-page")
        # Add a sub-root Page for group2
        cls.page2 = cls.rootPage.add_child(title="Group 2 Root Page", slug="g2-root")
        # Grant GroupPagePermission
        GroupPagePermission.objects.create(
            group=cls.group1, page=cls.page1, permission_type="edit"
        )
        GroupPagePermission.objects.create(
            group=cls.group2, page=cls.page2, permission_type="edit"
        )
        # Add a root Collection
        cls.rootCollection = Collection.add_root(name="Root Collection")
        # Add a sub-root Collection for group1
        cls.collection1 = cls.rootCollection.add_child(name="collection1")
        # Add a sub-root Collection for group2
        cls.collection2 = cls.rootCollection.add_child(name="collection2")
        # Although Wagtail UI does not yet support it (as of 2020-03-01), data model
        # supports nested collections.
        cls.collection3 = cls.collection1.add_child(name="collection3")
        # Grant GroupCollectionPermission
        GroupCollectionPermission.objects.create(
            group=cls.group1,
            collection=cls.collection1,
            permission=Permission.objects.get(codename="view_collection"),
        )
        GroupCollectionPermission.objects.create(
            group=cls.group2,
            collection=cls.collection2,
            permission=Permission.objects.get(codename="view_collection"),
        )
        # Add an image in root Collection
        Image = get_image_model()
        cls.image0 = Image.objects.create(
            title="image0", collection=cls.rootCollection, width=200, height=200
        )
        # Add an image in group1 Collection
        cls.image1 = Image.objects.create(
            title="image1", collection=cls.collection1, width=200, height=200
        )
        cls.image3 = Image.objects.create(
            title="image3", collection=cls.collection3, width=200, height=200
        )
        # Add an image in group2 Collection
        cls.image2 = Image.objects.create(
            title="image2", collection=cls.collection2, width=200, height=200
        )
        # Add a document in root Collection
        Document = get_document_model()
        cls.doc0 = Document.objects.create(
            title="document0", collection=cls.rootCollection
        )
        # Add a document in group1 Collection
        cls.doc1 = Document.objects.create(
            title="document1", collection=cls.collection1
        )
        cls.doc3 = Document.objects.create(
            title="document3", collection=cls.collection3
        )
        # Add a document in group2 Collection
        cls.doc2 = Document.objects.create(
            title="document2", collection=cls.collection2
        )

    def test_get_user_collections(self):
        """
        Regular users belonging to a group should see only collections with permissions
        """
        collections = hooks.get_user_collections(self.user1)
        assert collections.count() == 2
        assert self.collection1 in collections
        assert self.collection3 in collections

    def test_get_user_collections_multiroot(self):
        """
        Users in mutliple groups should see all their collections with permissions
        """
        collections = hooks.get_user_collections(self.user0)
        assert collections.count() == 3
        assert self.collection1 in collections
        assert self.collection2 in collections
        assert self.collection3 in collections

    def test_get_user_collections_superuser(self):
        """Superuser should see all collections"""
        collections = hooks.get_user_collections(self.superuser)
        # Correct answer is 5, not 4, because Wagtail's migrations create
        # another root collection.
        assert collections.count() == 5

    def test_document_filter(self):
        documents = get_document_model().objects.all()
        request = Mock(user=self.user1)

        newdocs = hooks.filter_documents_in_permitted_collections(documents, request)
        assert newdocs.count() == 2
        assert self.doc1 in newdocs
        assert self.doc3 in newdocs

    def test_document_filter_multiroot(self):
        documents = get_document_model().objects.all()
        request = Mock(user=self.user0)

        newdocs = hooks.filter_documents_in_permitted_collections(documents, request)
        assert newdocs.count() == 3
        assert self.doc1 in newdocs
        assert self.doc2 in newdocs
        assert self.doc3 in newdocs

    def test_document_filter_superuser(self):
        documents = get_document_model().objects.all()
        request = Mock(user=self.superuser)

        newdocs = hooks.filter_documents_in_permitted_collections(documents, request)
        assert newdocs.count() == 4
        assert self.doc0 in newdocs
        assert self.doc1 in newdocs
        assert self.doc2 in newdocs
        assert self.doc3 in newdocs

    def test_image_filter(self):
        images = get_image_model().objects.all()
        request = Mock(user=self.user1)

        newimgs = hooks.filter_images_in_permitted_collections(images, request)
        assert newimgs.count() == 2
        assert self.image1 in newimgs
        assert self.image3 in newimgs

    def test_image_filter_multiroot(self):
        images = get_image_model().objects.all()
        request = Mock(user=self.user0)

        newimgs = hooks.filter_images_in_permitted_collections(images, request)
        assert newimgs.count() == 3
        assert self.image1 in newimgs
        assert self.image2 in newimgs
        assert self.image3 in newimgs

    def test_image_filter_superuser(self):
        images = get_image_model().objects.all()
        request = Mock(user=self.superuser)

        newimgs = hooks.filter_images_in_permitted_collections(images, request)
        assert newimgs.count() == 4
        assert self.image0 in newimgs
        assert self.image1 in newimgs
        assert self.image2 in newimgs
        assert self.image3 in newimgs

    def test_page_filter(self):
        pages = Page.objects.all()
        request = Mock(user=self.user1)

        newpages = hooks.filter_pages_by_group_permission(pages, request)
        assert newpages.count() == 2
        assert self.page1 in newpages
        assert self.page3 in newpages

    def test_page_filter_multiroot(self):
        pages = Page.objects.all()
        request = Mock(user=self.user0)

        newpages = hooks.filter_pages_by_group_permission(pages, request)
        assert newpages.count() == 3
        assert self.page1 in newpages
        assert self.page2 in newpages
        assert self.page3 in newpages

    def test_page_filter_superuser(self):
        pages = Page.objects.all()
        request = Mock(user=self.superuser)

        newpages = hooks.filter_pages_by_group_permission(pages, request)
        # Correct answer is 6 not 4, because Wagtail's migrations add 2
        assert newpages.count() == 6
        assert self.rootPage in newpages
        assert self.page1 in newpages
        assert self.page2 in newpages
        assert self.page3 in newpages
