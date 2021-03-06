# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from cosinnus.utils.dashboard import DashboardWidget, DashboardWidgetForm

from cosinnus_event.models import Event


class UpcomingEventsForm(DashboardWidgetForm):
    amount = forms.IntegerField(label="Amount", initial=5, min_value=0,
        help_text="0 means unlimited", required=False)


class UpcomingEvents(DashboardWidget):

    app_name = 'event'
    form_class = UpcomingEventsForm
    model = Event
    title = _('Upcoming Events')
    user_model_attr = None  # No filtering on user page
    widget_name = 'upcoming'

    def get_data(self):
        if self.request.user.is_authenticated():
            count = int(self.config['amount'])
            qs = self.get_queryset().select_related('group').all()
            if count != 0:
                qs = qs[:count]
        else:
            qs = []
        data = {
            'rows': qs,
            'no_data': _('No upcoming events'),
        }
        return render_to_string('cosinnus_event/widgets/upcoming.html', data)

    def get_queryset(self):
        qs = super(UpcomingEvents, self).get_queryset()
        return qs.filter(from_date__gte=now())
