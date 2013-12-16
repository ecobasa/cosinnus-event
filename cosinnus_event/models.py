# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import dateformat
from django.utils.encoding import force_unicode
from django.utils.formats import date_format
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from geoposition.fields import GeopositionField

from cosinnus.models import BaseTaggableObjectModel

from cosinnus_event.conf import settings
from cosinnus_event.managers import EventManager



def localize(value, format):
    if (not format) or ("FORMAT" in format):
        return date_format(localtime(value), format)
    else:
        return dateformat.format(localtime(value), format)


class Event(BaseTaggableObjectModel):

    SORT_FIELDS_ALIASES = [
        ('title', 'title'),
        ('from_date', 'from_date'),
        ('to_date', 'to_date'),
        ('city', 'city'),
        ('state', 'state'),
    ]

    STATE_SCHEDULED = 1
    STATE_VOTING_OPEN = 2
    STATE_CANCELED = 3

    STATE_CHOICES = (
        (STATE_SCHEDULED, _('Scheduled')),
        (STATE_VOTING_OPEN, _('Voting open')),
        (STATE_CANCELED, _('Canceled')),
    )

    from_date = models.DateTimeField(
        _(u'Start'), default=None, blank=True, null=True, editable=False)

    to_date = models.DateTimeField(
        _(u'End'), default=None, blank=True, null=True, editable=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_(u'Created by'),
        on_delete=models.PROTECT,
        related_name='events',
    )

    state = models.PositiveIntegerField(
        _(u'State'),
        choices=STATE_CHOICES,
        default=STATE_VOTING_OPEN,
        editable=False,
    )

    note = models.TextField(_(u'Note'), blank=True, null=True)

    suggestion = models.ForeignKey(
        'Suggestion',
        verbose_name=_(u'Event date'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selected_name',
    )

    location = GeopositionField(_(u'Location'), blank=True, null=True)

    street = models.CharField(_('Street'), blank=True, max_length=50, null=True)

    zipcode = models.PositiveIntegerField(_('ZIP code'), blank=True, null=True)

    city = models.CharField(_('City'), blank=True, max_length=50, null=True)

    public = models.BooleanField(_(u'Is public (on website)'))

    image = models.ImageField(
        _(u'Image'), upload_to='events', blank=True, null=True)

    url = models.URLField(_(u'URL'), blank=True, null=True)

    objects = EventManager()

    class Meta:
        ordering = ['from_date', 'to_date']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __unicode__(self):
        if self.state == Event.STATE_SCHEDULED:
            if self.single_day:
                return force_unicode(
                    u'Date: %(date)s - %(end)s (%(event)s)' % {
                        'date': localize(self.from_date, 'd. F Y h:i'),
                        'end': localize(self.to_date, 'h:i'),
                        'event': self.title,
                    }
                )
            return force_unicode(
                u'From: %(from)s - To: %(to)s (%(event)s)' % {
                    'from': localize(self.from_date, 'd. F Y h:i'),
                    'to': localize(self.to_date, 'd. F Y h:i'),
                    'event': self.title,
                }
            )
        return force_unicode(u'Pending event: %(event)s' % {
            'event': self.title,
        })

    def get_absolute_url(self):
        kwargs = {'group': self.group.slug, 'event': self.pk}
        return reverse('cosinnus:event:entry-detail', kwargs=kwargs)


    def set_suggestion(self, sugg=None, update_fields=['from_date', 'to_date', 'state', 'suggestion']):
        if sugg is None:
            # No suggestion selected or remove selection
            self.from_date = None
            self.to_date = None
            self.state = Event.STATE_VOTING_OPEN
            self.suggestion = None
        elif sugg.event.pk == self.pk:
            # Make sure to not assign a suggestion belonging to another event.
            self.from_date = sugg.from_date
            self.to_date = sugg.to_date
            self.state = Event.STATE_SCHEDULED
            self.suggestion = sugg
        else:
            return
        self.save(update_fields=update_fields)

    @property
    def single_day(self):
        return localtime(self.from_date).date() == localtime(self.to_date).date()

    def get_period(self):
        if self.single_day:
            return localize(self.from_date, "d.m.Y")
        else:
            return "%s - %s" % (localize(self.from_date, "d.m."), localize(self.to_date, "d.m.Y"))


class Suggestion(models.Model):
    from_date = models.DateTimeField(
        _(u'Start'), default=None, blank=False, null=False)

    to_date = models.DateTimeField(
        _(u'End'), default=None, blank=False, null=False)

    event = models.ForeignKey(
        Event,
        verbose_name=_(u'Event'),
        on_delete=models.CASCADE,
        related_name='suggestions',
    )

    count = models.PositiveIntegerField(
        pgettext_lazy('the subject', u'Votes'), default=0, editable=False)

    class Meta:
        ordering = ['event', '-count']
        unique_together = ('event', 'from_date', 'to_date')
        verbose_name = _('Suggestion')
        verbose_name_plural = _('Suggestions')

    def __unicode__(self):
        if self.single_day:
            return force_unicode(
                u'%(date)s - %(end)s (%(count)d)' % {
                    'date': localize(self.from_date, 'd. F Y H:i'),
                    'end': localize(self.to_date, 'H:i'),
                    'count': self.count,
                }
            )
        return force_unicode(u'%(from)s - %(to)s (%(count)d)' % {
            'from': localize(self.from_date, 'd. F Y H:i'),
            'to': localize(self.to_date, 'd. F Y H:i'),
            'count': self.count,
        })

    def get_absolute_url(self):
        return self.event.get_absolute_url()

    def update_vote_count(self, count=None):
        self.count = self.votes.count()
        self.save(update_fields=['count'])

    @property
    def single_day(self):
        return localtime(self.from_date).date() == localtime(self.to_date).date()


class Vote(models.Model):
    suggestion = models.ForeignKey(
        Suggestion,
        verbose_name=_(u'Suggestion'),
        on_delete=models.CASCADE,
        related_name='votes',
    )

    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_(u'Voter'),
        on_delete=models.CASCADE,
        related_name='votes',
    )

    class Meta:
        unique_together = ('suggestion', 'voter')
        verbose_name = pgettext_lazy('the subject', u'Vote')
        verbose_name_plural = pgettext_lazy('the subject', u'Votes')

    def __unicode__(self):
        return force_unicode(u'Vote for %(event)s: %(from)s - %(to)s' % {
            'event': self.suggestion.event.title,
            'from': localize(self.suggestion.from_date, 'd. F Y h:i'),
            'to': localize(self.suggestion.to_date, 'd. F Y h:i'),
        })

    def get_absolute_url(self):
        return self.suggestion.event.get_absolute_url()


@receiver(post_delete, sender=Vote)
def post_vote_delete(sender, **kwargs):
    try:
        kwargs['instance'].suggestion.update_vote_count()
    except Suggestion.DoesNotExist:
        pass


@receiver(post_save, sender=Vote)
def post_vote_save(sender, **kwargs):
    kwargs['instance'].suggestion.update_vote_count()