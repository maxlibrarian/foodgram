import base64
import imghdr
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Позволяет принимать изображения в формате Base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, b64 = data.split(';base64,')
            file_ext = header.split('/')[-1]
            decoded = base64.b64decode(b64)
            ext = imghdr.what(None, decoded) or file_ext
            file_name = f"{uuid.uuid4().hex}.{ext}"
            data = ContentFile(decoded, name=file_name)
        return super().to_internal_value(data)
