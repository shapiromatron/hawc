from wagtail import hooks
from wagtail.models import PageViewRestriction


@hooks.register("after_create_page")
def make_page_private_after_creation(request, page):
    PageViewRestriction.objects.create(page=page, restriction_type=PageViewRestriction.LOGIN)
