from django.contrib.contenttypes.models import ContentType
from tag.models import Tag, Tagging
import re


'''
value : object.tags.all() 한 값
object : object
user : 요청한 유저
raw_data : 원래 object에 들어있던 tag 로써 이게 있다는 것은 수정된 컨텐츠 라는 것
'''
def tag(values, object, user, sort, raw_data):
    if values:
        tags = values.split(',')
        for tag in tags:
            tag = re.split("\W+|_", tag)
            tag = ''.join(tag)
            if tag in raw_data:
               raw_data.remove(tag)
            else:
                tag_name = Tag.objects.get_or_create(name=tag)
                Tagging.objects.create(tag=tag_name[0], sort=sort, content_object=object, user=user)
        if raw_data:
            for tagging in raw_data:
                ct = ContentType.objects.get_for_model(object)
                tagging = Tagging.objects.get(content_type=ct, object_id=object.id, tag__name=tagging)
                tagging.delete()