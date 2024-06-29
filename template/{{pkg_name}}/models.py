from typing import TypeVar

from tortoise import fields as f
from tortoise.models import Model

ModelT = TypeVar("ModelT", bound=Model)


class User(Model):
    id = f.IntField(primary_key=True)
    login_name = f.CharField(max_length=12)
