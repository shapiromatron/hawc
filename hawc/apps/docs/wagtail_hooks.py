from wagtail import hooks
from wagtail.models import PageViewRestriction


@hooks.register("after_edit_page")
@hooks.register("after_publish_page")
def make_private_after_publish(request, page):
    if page.depth <= 2:
        PageViewRestriction.objects.update_or_create(
            page=page, defaults=dict(restriction_type=PageViewRestriction.LOGIN)
        )
