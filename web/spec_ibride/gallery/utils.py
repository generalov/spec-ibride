import math
# Tag weight distribution algorithms
LOGARITHMIC, LINEAR = 1, 2


def _calculate_thresholds(min_weight, max_weight, steps):
    delta = (max_weight - min_weight) / float(steps)
    return [min_weight + i * delta for i in range(1, steps + 1)]


def _calculate_tag_weight(weight, max_weight, distribution):
    """Logarithmic tag weight calculation is based on code from the.

    *Tag Cloud* plugin for Mephisto, by Sven Fuchs.

    http://www.artweb-design.de/projects/mephisto-plugin-tag-cloud

    """
    if distribution == LINEAR or max_weight == 1:
        return weight
    elif distribution == LOGARITHMIC:
        return math.log(weight) * max_weight / math.log(max_weight)
    raise ValueError(
        _('Invalid distribution algorithm specified: %s.') % distribution)


def calculate_cloud(tags, steps=4, distribution=LOGARITHMIC):
    """Add a ``weight`` attribute to each tag according to the frequency of its
    use, as indicated by its ``count`` attribute.

    ``steps`` defines the range of font sizes - ``weight`` will
    be an integer between 1 and ``steps`` (inclusive).

    ``distribution`` defines the type of font size distribution
    algorithm which will be used - logarithmic or linear. It must be
    one of ``LOGARITHMIC`` or ``LINEAR``.

    """
    if len(tags) > 0:
        counts = [tag.count for tag in tags]
        min_weight = float(min(counts))
        max_weight = float(max(counts))
        thresholds = _calculate_thresholds(min_weight, max_weight, steps)
        for tag in tags:
            font_set = False
            tag_weight = _calculate_tag_weight(
                tag.count, max_weight, distribution)
            for i in range(steps):
                if not font_set and tag_weight <= thresholds[i]:
                    tag.weight = i + 1
                    font_set = True
    return tags
