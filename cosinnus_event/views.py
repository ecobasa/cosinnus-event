# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.utils.timezone import now

from extra_views import (CreateWithInlinesView, FormSetView, InlineFormSet,
    UpdateWithInlinesView, SortableListMixin)

from cosinnus.views.export import CSVExportView
from cosinnus.views.mixins.group import (RequireReadMixin, RequireWriteMixin,
    GroupFormKwargsMixin, FilterGroupMixin)
from cosinnus.views.mixins.tagged import TaggedListMixin
from cosinnus.views.mixins.user import UserFormKwargsMixin

from cosinnus.views.attached_object import AttachableViewMixin

from cosinnus_event.conf import settings
from cosinnus_event.forms import EventForm, SuggestionForm, VoteForm
from cosinnus_event.models import Event, Suggestion, Vote


class EventIndexView(RequireReadMixin, RedirectView):

    def get_redirect_url(self, **kwargs):
        return reverse('cosinnus:event:list', kwargs={'group': self.group.slug})

index_view = EventIndexView.as_view()


class EventListView(RequireReadMixin, FilterGroupMixin, TaggedListMixin,
                    SortableListMixin, ListView):

    model = Event
    
    def get_queryset(self):
        """ In the calendar we only show scheduled events """
        qs = super(EventListView, self).get_queryset()
        qs = qs.filter(state=Event.STATE_SCHEDULED)
        return qs
    
    def get(self, request, *args, **kwargs):
        self.sort_fields_aliases = self.model.SORT_FIELDS_ALIASES
        return super(EventListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        past_events = []
        future_events = []
        doodle_count = Event.objects.filter(state=Event.STATE_VOTING_OPEN).count()

        for event in context['object_list']:
            if (event.to_date and event.to_date < now()) or \
                        (not event.to_date and event.from_date and event.from_date < now()):
                past_events.append(event)
            else:
                future_events.append(event)
        context.update({
            'past_events': past_events,
            'future_events': future_events,
            'doodle_count': doodle_count,
        })
        return context

list_view = EventListView.as_view()

class DetailedEventListView(EventListView):
    template_name = 'cosinnus_event/event_list_detailed.html'
    
detailed_list_view = DetailedEventListView.as_view()

class SuggestionInlineView(InlineFormSet):
    extra = 1
    form_class = SuggestionForm
    model = Suggestion


class EntryFormMixin(RequireWriteMixin, FilterGroupMixin, GroupFormKwargsMixin,
                     UserFormKwargsMixin):
    form_class = EventForm
    model = Event
    message_success = _('Event "%(title)s" was edited successfully.')
    message_error = _('Event "%(title)s" could not be edited.')

    def dispatch(self, request, *args, **kwargs):
        self.form_view = kwargs.get('form_view', None)
        return super(EntryFormMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EntryFormMixin, self).get_context_data(**kwargs)
        tags = Event.objects.tags()
        context.update({
            'tags': tags,
            'form_view': self.form_view,
        })
        return context

    def get_success_url(self):
        kwargs = {'group': self.group.slug}
        # no self.object if get_queryset from add/edit view returns empty
        if hasattr(self, 'object'):
            kwargs['slug'] = self.object.slug
            urlname = 'cosinnus:event:event-detail'
        else:
            urlname = 'cosinnus:event:list'
        return reverse(urlname, kwargs=kwargs)

    def forms_valid(self, form, inlines):
        ret = super(EntryFormMixin, self).forms_valid(form, inlines)
        messages.success(self.request,
            self.message_success % {'title': self.object.title})
        return ret

    def forms_invalid(self, form, inlines):
        ret = super(EntryFormMixin, self).forms_invalid(form, inlines)
        if self.object:
            messages.error(self.request,
                self.message_error % {'title': self.object.title})
        return ret


class DoodleFormMixin(EntryFormMixin):
    inlines = [SuggestionInlineView]
    template_name = "cosinnus_event/doodle_form.html"

class EntryAddView(EntryFormMixin, AttachableViewMixin, CreateWithInlinesView):
    message_success = _('Event "%(title)s" was added successfully.')
    message_error = _('Event "%(title)s" could not be added.')
    
    def forms_valid(self, form, inlines):
        form.instance.creator = self.request.user
        
        # events are created as scheduled. doodle events would be created as VOTING
        form.instance.state = Event.STATE_SCHEDULED
        return super(EntryAddView, self).forms_valid(form, inlines)
    
entry_add_view = EntryAddView.as_view()


class DoodleAddView(DoodleFormMixin, AttachableViewMixin, CreateWithInlinesView):
    message_success = _('Event "%(title)s" was added successfully.')
    message_error = _('Event "%(title)s" could not be added.')

    def forms_valid(self, form, inlines):
        form.instance.creator = self.request.user

        ret = super(DoodleAddView, self).forms_valid(form, inlines)

        # Check for non or a single suggestion and set it and inform the user
        num_suggs = self.object.suggestions.count()
        if num_suggs == 0:
            messages.info(self.request,
                _('You should define at least one date suggestion.'))
        elif num_suggs == 1:
            self.object.set_suggestion(self.object.suggestions.get())
            messages.info(self.request,
                _('Automatically selected the only given date suggestion '
                  'as event date.'))
        return ret

doodle_add_view = DoodleAddView.as_view()


class EntryEditView(EntryFormMixin, AttachableViewMixin, UpdateWithInlinesView):
    pass

entry_edit_view = EntryEditView.as_view()


class DoodleEditView(DoodleFormMixin, AttachableViewMixin, UpdateWithInlinesView):

    def forms_valid(self, form, inlines):
        # Save the suggestions first so we can directly
        # access the amount of suggestions afterwards
        for formset in inlines:
            formset.save()

        suggestion = form.cleaned_data.get('suggestion')
        if not suggestion:
            num_suggs = form.instance.suggestions.count()
            if num_suggs == 0:
                suggestion = None
                messages.info(self.request,
                    _('You should define at least one date suggestion.'))
            elif num_suggs == 1:
                suggestion = form.instance.suggestions.get()
                messages.info(self.request,
                    _('Automatically selected the only given date suggestion '
                      'as event date.'))
        # update_fields=None leads to saving the complete model, we
        # don't need to call obj.self here
        # INFO: set_suggestion saves the instance
        form.instance.set_suggestion(suggestion, update_fields=None)
        
        return super(DoodleEditView, self).forms_valid(form, inlines)

doodle_edit_view = DoodleEditView.as_view()



class EntryDeleteView(EntryFormMixin, DeleteView):
    message_success = _('Event "%(title)s" was deleted successfully.')
    message_error = _('Event "%(title)s" could not be deleted.')

    def get_success_url(self):
        return reverse('cosinnus:event:list', kwargs={'group': self.group.slug})

entry_delete_view = EntryDeleteView.as_view()


class EntryDetailView(RequireReadMixin, FilterGroupMixin, DetailView):

    model = Event

    def get_context_data(self, **kwargs):
        context = super(EntryDetailView, self).get_context_data(**kwargs)
        height = getattr(settings, 'GEOPOSITION_MAP_WIDGET_HEIGHT', 200)
        context.update({
            'map_widget_height': height,
        })
        return context

entry_detail_view = EntryDetailView.as_view()


class EntryVoteView(RequireWriteMixin, FilterGroupMixin, SingleObjectMixin,
        FormSetView):

    extra = 0
    form_class = VoteForm
    model = Event
    template_name = 'cosinnus_event/vote_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super(EntryVoteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EntryVoteView, self).get_context_data(**kwargs)
        context.update({
            'object': self.object,
            'suggestions': self.suggestions,
        })
        return context

    def get_initial(self):
        self.object = self.get_object()
        self.suggestions = self.object.suggestions.order_by('from_date',
                                                            'to_date').all()
        self.max_num = self.suggestions.count()
        self.initial = []
        for suggestion in self.suggestions:
            vote = suggestion.votes.filter(voter=self.request.user).exists()
            self.initial.append({
                'suggestion': suggestion.pk,
                'vote': 1 if vote else 0,
            })
        return self.initial

    def get_success_url(self):
        kwargs = {'group': self.group.slug, 'slug': self.object.slug}
        return reverse('cosinnus:event:event-detail', kwargs=kwargs)

    def formset_valid(self, formset):
        for form in formset:
            cd = form.cleaned_data
            suggestion = int(cd.get('suggestion'))
            selection = int(cd.get('vote', 0))
            if selection:
                Vote.objects.get_or_create(suggestion_id=suggestion,
                                           voter=self.request.user)
            else:
                Vote.objects.filter(suggestion_id=suggestion,
                                    voter=self.request.user).delete()
        return super(EntryVoteView, self).formset_valid(formset)

entry_vote_view = EntryVoteView.as_view()


class EventExportView(CSVExportView):
    fields = [
        'from_date',
        'to_date',
        'creator',
        'state',
        'note',
        'location',
        'street',
        'zipcode',
        'city',
        'public',
        'image',
        'url',
    ]
    model = Event
    file_prefix = 'cosinnus_event'

export_view = EventExportView.as_view()
