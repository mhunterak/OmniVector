'''
Models

- Project
- Stage
- Activity

Projects may have one or more stages, stages may have one or more 
activities. Outside of their relationships to each other, each 
object need only contain “name" and “description” attributes.

'''

from peewee import *

DATABASE = SqliteDatabase(None)


class Project(Model):
    name = CharField(max_length=32)
    description = CharField(max_length=128)

    class Meta:
        database = DATABASE


class Stage(Model):
    name = CharField(max_length=32)
    description = CharField(max_length=128)
    project = ForeignKeyField(Project, related_name='stages')

    class Meta:
        database = DATABASE


class Activity(Model):
    name = CharField(max_length=32)
    description = CharField(max_length=128)
    stage = ForeignKeyField(Stage, related_name='activities')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.init('DB.sqlite')
    DATABASE.connect()
    DATABASE.create_tables(
        [Project, Stage, Activity],
        safe=True)
    DATABASE.close()
