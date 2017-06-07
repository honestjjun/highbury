from django.conf import settings

from PIL import Image
import os, re


# summernote 입력시 body에서 이미지 파일을 꺼내서 리사이징 하기
def value(values):
    post_body_lists = re.findall('src="([^"]+)"', values)
    if post_body_lists:
        for post_body_list in post_body_lists:
            post_body_root = post_body_list.replace('/media/','')
            image = Image.open(os.path.join(settings.MEDIA_ROOT, post_body_root))
            if image.width > 698:
                t_ratio = round(690/image.width, 2)
                image_width = int(image.width * t_ratio)
                image_height = int(image.height * t_ratio)
                image = image.resize((image_width, image_height), Image.ANTIALIAS)
                image.save(settings.MEDIA_ROOT+post_body_root, format='JPEG', quality=70)
            else:
                image.save(settings.MEDIA_ROOT+post_body_root, format='JPEG', quality=70)
        return values
    else:
        return values


def find_src(posts, post_body):
    for post in posts:
        # post.body 에서 src 로 시작된 문구 뽑아내기
        post_body_img_list = re.findall('src="([^"]+)"', post.body)
        for post_body_img in post_body_img_list:
            # src 에 있는 /media/ 를 없애기
            post_body_img = post_body_img.replace('/media/', '')
            post_body.append(post_body_img)
    return post_body