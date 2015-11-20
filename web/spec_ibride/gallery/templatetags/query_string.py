# -*- coding: utf-8 -*-
"""
make_query_string template tag from http://stackoverflow.com/a/16411043/3297887
"""
from django import template
from django.utils.encoding import force_text  # Django 1.5+ only

register = template.Library()


class QueryStringNode(template.Node):

    def __init__(self, tag_name, parsed_args, var_name=None, silent=False):
        self.tag_name = tag_name
        self.parsed_args = parsed_args
        self.var_name = var_name
        self.silent = silent

    def render(self, context):
        # django.core.context_processors.request should be enabled in
        # settings.TEMPLATE_CONTEXT_PROCESSORS.
        # Or else, directly pass the HttpRequest object as 'request' in
        # context.
        query_dict = context['request'].GET.copy()
        for op, key, value in self.parsed_args:
            if op == '+':
                query_dict.appendlist(key, value.resolve(context))
            elif op == '-':
                list_ = query_dict.getlist(key)
                value_ = value.resolve(context)
                try:
                    list_.remove(value_)
                except ValueError:
                    # Value not found
                    if not isinstance(value_, basestring):
                        # Try to convert it to unicode, and try again
                        try:
                            list_.remove(force_text(value_))
                        except ValueError:
                            pass
            elif op == 'd':
                try:
                    del query_dict[key]
                except KeyError:
                    pass
            else:
                query_dict[key] = value.resolve(context)
        query_string = query_dict.urlencode()
        if self.var_name:
            context[self.var_name] = query_string
        if self.silent:
            return ''
        return query_string


@register.tag
def make_query_string(parser, token):
    # {% make_query_string page=1 size= item+="foo" item-="bar" as foo [silent] %}
    args = token.split_contents()
    tag_name = args[0]
    as_form = False
    if len(args) > 3 and args[-3] == 'as':
        # {% x_make_query_string ... as foo silent %} case.
        if args[-1] != 'silent':
            raise template.TemplateSyntaxError(
                "Only 'silent' flag is allowed after %s's name, not '%s'." %
                (tag_name, args[-1]))
        as_form = True
        silent = True
        args = args[:-1]
    elif len(args) > 2 and args[-2] == 'as':
        # {% x_make_query_string ... as foo %} case.
        as_form = True
        silent = False

    if as_form:
        var_name = args[-1]
        raw_pairs = args[1:-2]
    else:
        raw_pairs = args[1:]

    parsed_args = []
    for pair in raw_pairs:
        try:
            arg, raw_value = pair.split('=', 1)
        except ValueError:
            raise template.TemplateSyntaxError(
                "%r tag's argument should be in format foo=bar" % tag_name)
        operator = arg[-1]
        if operator == '+':
            # item+="foo": Append to current query arguments.
            # e.g. item=1 -> item=1&item=foo
            parsed_args.append(
                ('+', arg[:-1], parser.compile_filter(raw_value)))
        elif operator == '-':
            # item-="bar": Remove from current query arguments.
            # e.g. item=1&item=bar -> item=1
            parsed_args.append(
                ('-', arg[:-1], parser.compile_filter(raw_value)))
        elif raw_value == '':
            # item=: Completely remove from current query arguments.
            # e.g. item=1&item=2 -> ''
            parsed_args.append(('d', arg, None))
        else:
            # item=1: Replace current query arguments, e.g. item=2 -> item=1
            parsed_args.append(('', arg, parser.compile_filter(raw_value)))

    if as_form:
        node = QueryStringNode(tag_name, parsed_args,
                               var_name=var_name, silent=silent)
    else:
        node = QueryStringNode(tag_name, parsed_args)

    return node
