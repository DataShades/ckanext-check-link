import factory
import pytest
from pytest_factoryboy import register

from ckan.tests.factories import CKANFactory, Resource, fake

from ckanext.check_link.model import Report


@pytest.fixture()
def clean_db(reset_db, migrate_db_for):
    reset_db()
    migrate_db_for("check_link")


@register
class ReportFactory(CKANFactory):
    """A factory class for creating CKAN users."""

    class Meta:
        model = Report
        action = "check_link_report_save"

    # These are the default params that will be used to create new users.
    url = factory.LazyFunction(fake.url)
    resource_id = factory.LazyFunction(lambda: Resource()["id"])
    state = "available"
