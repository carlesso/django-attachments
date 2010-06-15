from datetime import datetime
import os
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

class AttachmentManager(models.Manager):
    def get_for_tag(self, obj, tag):
        object_type = ContentType.objects.get_for_model(obj)
        print tag
        print self.filter(content_type__pk = object_type.id, object_id = obj.id)
        try:
            return self.get(content_type__pk = object_type.id,
                            object_id = obj.id,
                            tag = tag)
        except: # Maybe DoesNotExist is more appropiate?
            return False

    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id,
                           object_id=obj.id)

class Attachment(models.Model):
    def attachment_upload(instance, filename):
        """Stores the attachment in a "per module/appname/primary key" folder"""
        return 'attachments/%s/%s/%s' % (
            '%s_%s' % (instance.content_object._meta.app_label,
                       instance.content_object._meta.object_name.lower()),
                       instance.content_object.pk,
                       filename)

    objects = AttachmentManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    creator = models.ForeignKey(User, related_name="created_attachments", verbose_name=_('creator'))
    attachment_file = models.FileField(_('attachment'), upload_to=attachment_upload)

    tag = models.CharField(max_length = 30, null = True, blank = True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        ordering = ['-created']
        permissions = (
            ('delete_foreign_attachments', 'Can delete foreign attachments'),
        )

    def __unicode__(self):
        if self.tag:
            return '%s attached %s (%s)' % (self.creator.username, self.attachment_file.name, self.tag)
        return '%s attached %s' % (self.creator.username, self.attachment_file.name)

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]