
from django.db import models
from datetime import datetime
import uuid


def bake(model, **kwargs):
    """Simple bakery-like helper that creates and saves objects."""
    obj = model(**kwargs)
    obj.save()
    return obj


def m2m_bake(obj, related_model, **kwargs):
    """Helper to create through relationships."""
    if isinstance(related_model, list):
        for rel in related_model:
            obj.related.add(rel)
    elif hasattr(obj, f'related_{related_model._meta.model_name}'):
        getattr(obj, f'related_{related_model._meta.model_name}').set(obj.terms.filter(pk=related_model.pk))


def fake_user(email):
    """Create a fake HAWCUser."""
    from myuser.models import HAWCUser
    
    # Check if user exists
    try:
        return HAWCUser.objects.get(email=email)
    except HAWCUser.DoesNotExist:
        return HAWCUser.objects.create_user(
            email=email,
            username=email.split('@')[0],
            first_name='Test',
            last_name='User'
        )

