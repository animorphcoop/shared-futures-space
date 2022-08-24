# converting ClusterTaggableManager modelcluster.queryset.FakeQuerySet
# returns Wagtail tags (non-iterable) as a list within the objects passed


def objects_tags_cluster_list_overwrite(objects_set):
    for entry in objects_set:
        # overwriting tags key in the queryset
        if entry.tags:
            entry.tags = tag_cluster_to_list(entry.tags)

    return objects_set

def tag_cluster_to_list(tags):
    tag_list = []
    for tag in tags.all():
        tag_list.append(tag)

    return tag_list
