# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'cosinnus_event_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('media_tag', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cosinnus.TagObject'], unique=True, null=True, on_delete=models.PROTECT, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'cosinnus_event_event_set', on_delete=models.PROTECT, to=orm['auth.Group'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=55)),
            ('from_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('to_date', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'events', on_delete=models.PROTECT, to=orm['auth.User'])),
            ('state', self.gf('django.db.models.fields.PositiveIntegerField')(default=2)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('suggestion', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'selected_name', null=True, on_delete=models.SET_NULL, to=orm['cosinnus_event.Suggestion'])),
            ('location', self.gf('geoposition.fields.GeopositionField')(default='0,0', max_length=42, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'cosinnus_event', ['Event'])

        # Adding model 'Suggestion'
        db.create_table(u'cosinnus_event_suggestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_date', self.gf('django.db.models.fields.DateTimeField')(default=None)),
            ('to_date', self.gf('django.db.models.fields.DateTimeField')(default=None)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'suggestions', to=orm['cosinnus_event.Event'])),
            ('count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'cosinnus_event', ['Suggestion'])

        # Adding unique constraint on 'Suggestion', fields ['event', 'from_date', 'to_date']
        db.create_unique(u'cosinnus_event_suggestion', ['event_id', 'from_date', 'to_date'])

        # Adding model 'Vote'
        db.create_table(u'cosinnus_event_vote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('suggestion', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'votes', to=orm['cosinnus_event.Suggestion'])),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'votes', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'cosinnus_event', ['Vote'])

        # Adding unique constraint on 'Vote', fields ['suggestion', 'voter']
        db.create_unique(u'cosinnus_event_vote', ['suggestion_id', 'voter_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Vote', fields ['suggestion', 'voter']
        db.delete_unique(u'cosinnus_event_vote', ['suggestion_id', 'voter_id'])

        # Removing unique constraint on 'Suggestion', fields ['event', 'from_date', 'to_date']
        db.delete_unique(u'cosinnus_event_suggestion', ['event_id', 'from_date', 'to_date'])

        # Deleting model 'Event'
        db.delete_table(u'cosinnus_event_event')

        # Deleting model 'Suggestion'
        db.delete_table(u'cosinnus_event_suggestion')

        # Deleting model 'Vote'
        db.delete_table(u'cosinnus_event_vote')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cosinnus.tagobject': {
            'Meta': {'object_name': 'TagObject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'cosinnus_event.event': {
            'Meta': {'ordering': "[u'from_date', u'to_date']", 'object_name': 'Event'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'events'", 'on_delete': 'models.PROTECT', 'to': u"orm['auth.User']"}),
            'from_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'cosinnus_event_event_set'", 'on_delete': 'models.PROTECT', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'location': ('geoposition.fields.GeopositionField', [], {'default': "'0,0'", 'max_length': '42', 'null': 'True', 'blank': 'True'}),
            'media_tag': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cosinnus.TagObject']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '55'}),
            'state': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'suggestion': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'selected_name'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['cosinnus_event.Suggestion']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'cosinnus_event.suggestion': {
            'Meta': {'ordering': "[u'event', u'-count']", 'unique_together': "((u'event', u'from_date', u'to_date'),)", 'object_name': 'Suggestion'},
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'suggestions'", 'to': u"orm['cosinnus_event.Event']"}),
            'from_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None'})
        },
        u'cosinnus_event.vote': {
            'Meta': {'unique_together': "((u'suggestion', u'voter'),)", 'object_name': 'Vote'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'suggestion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'votes'", 'to': u"orm['cosinnus_event.Suggestion']"}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'votes'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['cosinnus_event']