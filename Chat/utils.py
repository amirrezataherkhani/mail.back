import os
import random
import string

from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def RandomString(length):
    letters_str = string.ascii_letters + string.digits
    letters = list(letters_str)
    return ''.join(random.choice(letters) for _ in range(length))


def upload_user_profilepic(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{RandomString(100)}{ext}"
    return f"{instance.chat.owner.id}/profile/{final_name}"


def upload_profilepic(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{RandomString(100)}{ext}"
    return f"{instance.owner.id}/profile/{final_name}"


def upload_banner(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{RandomString(100)}{ext}"
    return f"banner/{final_name}"


def upload_file(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{RandomString(100)}{ext}"
    return f"{instance.sender.id}/{final_name}"


def SlugChecker(cls):
    slug = RandomString(40)
    while True:
        qs = cls.objects.filter(slug=slug)
        if not qs.exists():
            break
    return slug


class CreateUpdateRetrieveDestroyAPIView(CreateAPIView, UpdateAPIView,
                                         RetrieveAPIView, DestroyAPIView):
    pass


class CreateRetrieveDestroyAPIView(CreateAPIView, UpdateAPIView,
                                   RetrieveAPIView, DestroyAPIView):
    pass
