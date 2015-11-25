import six

from django.db.models.query import RawQuerySet
from django.db import connections


class SizedRawQuerySet(RawQuerySet):
    """
    Provides an iterator which converts the results of raw SQL queries into
    annotated model instances with ``order_by`` and limits support.
    """

    def __init__(self, raw_query, model=None, query=None, params=None,
                 translations=None, using=None, hints=None):
        super(SizedRawQuerySet, self).__init__(
            raw_query=raw_query, model=model, query=query, params=params,
            translations=translations, using=using, hints=hints
        )
        self._result_cache = None
        if not hasattr(self.query, 'order_by'):
            self.query.order_by = []

    def count(self):
        if self._result_cache is not None:
            return len(self._result_cache)
        return self._get_count()

    def set_limits(self, qs, low=None, high=None):
        """
        Adjusts the limits on the rows retrieved. We use low/high to set these,
        as it makes it more Pythonic to read and write. When the SQL query is
        created, they are converted to the appropriate offset and limit values.

        Any limits passed in here are applied relative to the existing
        constraints. So low is added to the current low value and both will be
        clamped to any existing high value.
        """
        if high is not None:
            if qs.high_mark is not None:
                qs.high_mark = min(qs.high_mark, qs.low_mark + high)
            else:
                qs.high_mark = qs.low_mark + high
        if low is not None:
            if qs.high_mark is not None:
                qs.low_mark = min(qs.high_mark, qs.low_mark + low)
            else:
                qs.low_mark = qs.low_mark + low

    def order_by(self, *args):
        obj = self._clone()
        obj.query.order_by.extend(args[:])
        return obj

    def __iter__(self):
        if self._result_cache is not None:
            return iter(self._result_cache)
        return super(SizedRawQuerySet, self).__iter__()

    def __len__(self):
        self._fetch_all()
        return len(self._result_cache)

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, (slice,) + six.integer_types):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."

        if self._result_cache is not None:
            return self._result_cache[k]

        if isinstance(k, slice):
            qs = self._clone()
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None
            self.set_limits(qs.query, start, stop)
            return list(qs)[::k.step] if k.step else qs

        qs = self._clone()
        self.set_limits(qs.query, k, k + 1)
        return list(qs)[0]

    def _clone(self, klass=None, setup=False, **kwargs):
        base_queryset_class = getattr(self, '_base_queryset_class', self.__class__)
        if klass is None:
            klass = self.__class__
        elif not (issubclass(base_queryset_class, klass) or issubclass(klass, base_queryset_class)):
            class_bases = (klass, base_queryset_class)
            class_dict = {
                '_base_queryset_class': base_queryset_class,
                '_specialized_queryset_class': klass,
            }
            klass = type(klass.__name__, class_bases, class_dict)

        query = self.query.clone(using=self._db)
        query.high_mark = self.query.high_mark
        query.low_mark = self.query.low_mark
        query.order_by = self.query.order_by[:]

        # if self._sticky_filter:
        #     query.filter_is_sticky = True
        c = klass(
            self.raw_query, model=self.model, query=query, params=self.params,
            translations=self.translations, using=self._db, hints=self._hints)
        # c._for_write = self._for_write
        # c._prefetch_related_lookups = self._prefetch_related_lookups[:]
        # c._known_related_objects = self._known_related_objects
        c.__dict__.update(kwargs)
        if setup and hasattr(c, '_setup_query'):
            c._setup_query()
        return c

    def _get_count(self):
        from django.db import connection
        sql = 'SELECT COUNT(*) FROM (' + self.raw_query + ') B'
        cursor = connection.cursor()
        cursor.execute(sql, params=self.params)
        row = cursor.fetchone()
        return row[0]

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self.iterator())

    def iterator(self):
        """
        An iterator over the results from applying this QuerySet to the
        database.
        """
        db = self._db
        connection = connections[db]
        model = self.model
        query = self.query
        self._compile(model, query, connection)

        return iter(self)

    @staticmethod
    def _compile(model, query, connection):
        """
        Apply to query ORDER BY and LIMIT.

        :param model:
        :param query:
        :param connection:
        :return:
        """
        result = [query.sql]
        order_by = query.order_by
        if order_by:
            db_table = connection.ops.quote_name(model._meta.db_table)
            ordering = []
            for field_desc in order_by:
                if field_desc[0] == '-':
                    direction, field = 'DESC', field_desc[1:]
                else:
                    direction, field = 'ASC', field_desc[1:]
                o_sql = '{}.{} {}'.format(db_table, connection.ops.quote_name(field), direction)
                ordering.append(o_sql)
            result.append('ORDER BY %s' % ', '.join(ordering))
        if query.high_mark is not None:
            result.append('LIMIT %d' % (query.high_mark - query.low_mark))
        if query.low_mark:
            if query.high_mark is None:
                val = connection.ops.no_limit_value()
                if val:
                    result.append('LIMIT %d' % val)
            result.append('OFFSET %d' % query.low_mark)
        query.sql = ' '.join(result)
