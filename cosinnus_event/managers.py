# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now

from taggit.models import TaggedItem


class EventManager(models.Manager):
    def public(self):
        return self.get_query_set().filter(public=True, state=self.model.STATE_SCHEDULED)

    def upcoming(self, count):
        return self.public().filter(to_date__gte=now()).order_by("from_date").all()[:count]

    def tags(self):
        event_type = ContentType.objects.get(app_label="cosinnus_event", model="event")

        tag_names = []
        for ti in TaggedItem.objects.filter(content_type_id=event_type):
            if not ti.tag.name in tag_names:
                tag_names.append(ti.tag.name)

        return tag_names
