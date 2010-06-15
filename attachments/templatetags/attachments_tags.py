from django.template import Library, Node, Variable, VariableDoesNotExist
from attachments.forms import AttachmentForm, AttachmentFormWithTag
from attachments.views import add_url_for_obj
from django.core.urlresolvers import reverse
from attachments.models import Attachment

register = Library()

@register.inclusion_tag('attachments/add_form.html', takes_context=True)
def attachment_form(context, obj):
    """
    Renders a "upload attachment" form.
    
    If "next" is set in the context will be used as redirect after upload.

    The user must own ``attachments.add_attachment permission`` to add
    attachments.
    """
    try:
        next = Variable('next').resolve(context)
    except VariableDoesNotExist:
        next = context['request'].build_absolute_uri(),
    if context['user'].has_perm('attachments.add_attachment'):
        return {
            'form': AttachmentForm(),
            'form_url': add_url_for_obj(obj),
            'next': next,
        }
    else:
        return {
            'form': None,
        }

@register.inclusion_tag('attachments/add_form.html', takes_context=True)
def attachment_form_with_tag(context, obj, tag):
    """
    Renders a "upload attachment" form whith and hidden field for tag.

    If "next" is set in the context will be used as redirect after upload.
    
    The user must own ``attachments.add_attachment permission`` to add
    attachments.
    """
    try:
        next = Variable('next').resolve(context)
    except VariableDoesNotExist:
        next = context['request'].build_absolute_uri(),
    if context['user'].has_perm('attachments.add_attachment'):
        return {
            'form': AttachmentFormWithTag(initial = {'tag': tag}),
            'form_url': add_url_for_obj(obj),
            'next': next,
        }
    else:
        return {
            'form': None,
        }


@register.inclusion_tag('attachments/delete_link.html', takes_context=True)
def attachment_delete_link(context, attachment):
    """
    Renders a html link to the delete view of the given attachment. Returns
    no content if the request-user has no permission to delete attachments.
    
    The user must own either the ``attachments.delete_attachment`` permission
    and is the creator of the attachment, that he can delete it or he has
    ``attachments.delete_foreign_attachments`` which allows him to delete all
    attachments.
    """
    if context['user'].has_perm('delete_foreign_attachments') \
       or (context['user'] == attachment.creator and \
           context['user'].has_perm('attachments.delete_attachment')):
        return {
            'next': context['request'].build_absolute_uri(),
            'delete_url': reverse('delete_attachment', kwargs={'attachment_pk': attachment.pk})
        }
    return {'delete_url': None,}



class AttachmentsForObjectNode(Node):
    def __init__(self, obj, var_name):
        self.obj = obj
        self.var_name = var_name

    def resolve(self, var, context):
        """Resolves a variable out of context if it's not in quotes"""
        if var[0] in ('"', "'") and var[-1] == var[0]:
            return var[1:-1]
        else:
            return Variable(var).resolve(context)

    def render(self, context):
        obj = self.resolve(self.obj, context)
        var_name = self.resolve(self.var_name, context)
        context[var_name] = Attachment.objects.attachments_for_object(obj)
        return ''

class AttachmentWithTagForObjectNode(Node):
    def __init__(self, obj, tag, var_name):
        self.obj = obj
        self.tag = tag
        self.var_name = var_name

    def resolve(self, var, context):
        """Resolves a variable out of context if it's not in quotes"""
        if var[0] in ('"', "'") and var[-1] == var[0]:
            return var[1:-1]
        else:
            return Variable(var).resolve(context)

    def render(self, context):
        obj = self.resolve(self.obj, context)
        tag = self.resolve(self.tag, context)
        var_name = self.resolve(self.var_name, context)
        print self.tag
        context[var_name] = Attachment.objects.get_for_tag(obj, tag)
        return ''


@register.tag
def get_attachments_for(parser, token):
    """
    Resolves attachments that are attached to a given object. You can specify
    the variable name in the context the attachments are stored using the `as`
    argument. Default context variable name is `attachments`.

    Syntax::

        {% get_attachments_for obj %}
        {% for att in attachments %}
            {{ att }}
        {% endfor %}

        {% get_attachments_for obj as "my_attachments" %}

    """
    def next_bit_for(bits, key, if_none=None):
        try:
            return bits[bits.index(key)+1]
        except ValueError:
            return if_none

    bits = token.contents.split()
    args = {
        'obj': next_bit_for(bits, 'get_attachments_for'),
        'var_name': next_bit_for(bits, 'as', '"attachments"'),
    }
    return AttachmentsForObjectNode(**args)

@register.tag
def get_attachment_with_tag(parser, token):
    """
    Retrive attachment with tag that is attached to a given object. You can specify
    the variable name in the context the attachments are stored using the `as`
    argument. Default context variable name is `attachment`.

    Syntax::

        {% get_attachment_with_tag obj tag %}
        {{ attachments }}

        {% get_attachments_with_tag obj tag as "my_attachment" %}

    """
    # def next_bit_for(bits, key, if_none=None):
    #     print bits
    #     try:
    #         return bits[bits.index(key)+1]
    #     except ValueError:
    #         return if_none

    # bits = token.contents.split()
    # args = {
    #     'obj': next_bit_for(bits, 'get_attachment_with_tag'),
    #     'tag': next_bit_for(bits, 'obj'),
    #     'var_name': next_bit_for(bits, 'as', '"attachments"'),
    # }
    # print args
    bits = token.contents.split()
    args = {
        'obj': bits[1],
        'tag': bits[2],
        'var_name': bits[4] if len(bits) > 3 else bits[2]
        }
    print args
    return AttachmentWithTagForObjectNode(**args)
