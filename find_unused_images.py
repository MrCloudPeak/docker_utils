#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

IMAGES_COMMAND = 'docker images'
PS_COMMAND = 'docker ps -a'
HISTORY = 'docker history %s'
RE = re.compile(r'\s+\s+')


def exec_command(command):
    result = os.popen(command)
    return result.readlines()


class Image(object):
    def __init__(self, image_info):
        self.split_info = RE.split(image_info)
        self.image_id = self.split_info[2]
        self._generate_image_name()
        self.size = self.split_info[-1]

    def _generate_image_name(self):
        tag = self.split_info[1]
        repo = self.split_info[0]
        self.name = repo if tag == 'latest' else repo + ':' + tag

    def get_related_images(self):
        image_ids = [RE.split(history)[0] for history in exec_command(HISTORY % self.image_id)[1:] if
                     RE.split(history)[0] != '<missing>']
        return filter(None, [ImageUtil.get_image_by_id(image_id) for image_id in image_ids])

    def __repr__(self):
        return 'id:%s name:%s size:%s' % (self.image_id, self.name, self.size)

    def __hash__(self):
        return hash(self.image_id)

    def __eq__(self, other):
        return self.image_id == other.image_id

    def __ne__(self, other):
        return not self.__eq__(other)


class ImageUtil(object):
    all_images = [Image(image_info) for image_info in exec_command(IMAGES_COMMAND)[1:]]

    @classmethod
    def get_image_by_id(cls, image_id):
        try:
            return filter(lambda img: img.image_id == image_id, cls.all_images)[0]
        except IndexError:
            return ''

    @classmethod
    def get_image_by_name(cls, name):
        try:
            return filter(lambda img: img.name == name, cls.all_images)[0]
        except IndexError:
            return ''


class Container(object):
    def __init__(self, container_info):
        self.split_info = RE.split(container_info)
        image_name = self.split_info[1]
        self.image = ImageUtil.get_image_by_name(image_name)


class ContainerUtil(object):
    all_containers = [Container(container_info) for container_info in exec_command(PS_COMMAND)[1:]]

    @classmethod
    def get_used_images(cls):
        used_images = [container.image for container in cls.all_containers if container.image]
        related_images = []
        for used_image in used_images:
            related_images.extend(used_image.get_related_images())
        used_images.extend(related_images)
        return used_images


if __name__ == '__main__':
    all_images = ImageUtil.all_images
    images_used_by_container = ContainerUtil.get_used_images()
    unused_images = set(all_images) - set(images_used_by_container)
    print('unused images')
    for image in unused_images:
        print(image)
