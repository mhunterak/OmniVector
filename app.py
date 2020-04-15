'''
Use your choice of python web frameworks to create an nested web api that
models the following objects:

- Project
- Stage
- Activity

Projects may have one or more stages, stages may have one or more
activities. Outside of their relationships to each other, each
object need only contain “name" and “description” attributes.



The endpoints that need to be implemented are as follows:

/projects/ - GET
/projects/{pk}/ - GET, PUT, POST, DELETE
/projects/{project_pk}/stages/ - GET
/projects/{project_pk}/stages/{stage_pk}/ - GET, PUT, POST, DELETE
/projects/{project_pk}/stages/{stage_pk}/activities/ - GET
/projects/{project_pk}/stages/{stage_pk}/activities/{pk}/
    - GET, PUT, POST, DELETE
'''

import json

from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort
from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model

import models

# TODO: these should come from ENV vars in production
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

app = Flask(__name__)
api = Api(app)


@app.before_request
def before_request():
    models.DATABASE.connect()


@app.after_request
def after_request(response):
    models.DATABASE.close()
    return response


# ###### #
# ROUTES #
# ###### #

# 1. Projects
# ###

class Projects(Resource):
    '''
    This generic endpoint is used for getting a list of all projects,
    and for posting a new project.
    '''
    # /projects/ - GET

    def get(self):
        '''
        gets all Projects
        '''
        projects = models.Project.select()
        return_array = []
        for project in projects:
            return_array.append(model_to_dict(project))
        return {'projects': json.dumps(return_array)}

    # XTRA - /projects/- POST
    def post(self):
        '''
        Though this wasn't requested, I think a posting new data here is the best way to make a new project.
        '''
        project = models.Project.create(
            name=request.form['name'],
            description=request.form['description']
        )
        return {'project': model_to_dict(project)}, 201


api.add_resource(Projects, '/projects/')


class Project(Resource):
    '''
    This endpoint handles interactions with one specific project, designated
    by pk.
    '''
    # /projects/{pk} - GET, PUT, POST, DELETE

    def get(self, pk):
        try:
            project = models.Project.get(pk)
            return {'projects': model_to_dict(project)}
        except DoesNotExist:
            abort(404)

    def put(self, pk):
        project = models.Project.get(pk)
        if request.form['name']:
            project.name = request.form['name']
        if request.form['description']:
            project.description = request.form['description']
        project.save()

        return {'project': model_to_dict(project)}, 202

    def post(self, pk):
        '''
        Actually makes a Stage
        '''
        stage = models.Stage.create(
            project=pk,
            name=request.form['name'],
            description=request.form['description']
        ), 201

    def delete(self, pk):
        try:
            project = models.Project.get(pk)
        except DoesNotExist:
            return abort(404)
        project.delete_instance(recursive=True)
        return '', 204


api.add_resource(Project, '/project/<int:pk>')


# 2. Stages
# ###


class Stages(Resource):
    '''
    This generic endpoint is used for getting a list of all stages for a
    specific project, and for posting a new stage.
    # /projects/{project_pk}/stages - GET
    '''

    def get(self, project_pk):
        '''
        gets all stages for a project
        '''
        stages = models.Stage.select().where(models.Stage.project == project_pk)
        return_array = []
        for stage in stages:
            return_array.append(model_to_dict(stage))
        return {'stages': json.dumps(return_array)}

    def post(self, project_pk):
        '''
        # /projects/{project_pk}/stages POST
        Though this wasn't requested, I propose posting new data here is the
        best place to make a new stage
        '''
        stage = models.Stage.create(
            name=request.form['name'],
            description=request.form['description'],
            project=project_pk
        )
        return {'stage': model_to_dict(stage)}, 201


api.add_resource(Stages, '/projects/<int:project_pk>/stages')


class Stage(Resource):
    '''
    # /projects/{project_pk}/stages/{stage_pk} - GET, PUT, POST, DELETE
    '''

    def get(self, project_pk, stage_pk):
        try:
            project = models.Project.get(project_pk)
            stage = models.Stage.get(stage_pk)
            return {
                'project': model_to_dict(project),
                'stages': model_to_dict(stage)
            }
        except DoesNotExist:
            abort(404)

    def put(self, project_pk, stage_pk):
        project = models.Project.get(project_pk)
        stage = models.Stage.get(stage_pk)
        if request.form['name']:
            stage.name = request.form['name']
        if request.form['description']:
            stage.description = request.form['description']
        stage.save()
        return {'stage': model_to_dict(stage)}, 202

    def post(self, project_pk, stage_pk):
        '''
        actually makes an Activity
        '''
        activity = models.Activity.create(
            stage=stage_pk,
            name=request.form['name'],
            description=request.form['description']
        ), 201
        return {'stage': model_to_dict(stage)}, 202

    def delete(self, project_pk, stage_pk):
        try:
            stage = models.Stage.get(stage_pk)
        except DoesNotExist:
            return abort(404)
        if stage.project == project_pk:
            stage.delete_instance(recursive=True)
            return '', 204
        return 'Project pk and stage project do not match.', 403


api.add_resource(Stage, '/projects/<project_pk>/stages/<stage_pk>')


# 3. Activities
# ###


class Activities(Resource):
    '''
    This generic endpoint is used for getting a list of all activites for a
    stage, and for posting a new activity.
    # /projects/{project_pk}/stages/{stage_pk}/activities/ - GET
    '''

    def get(self, project_pk, stage_pk):
        '''
            gets all activities
        '''
        activities = models.Activity.select().where(
            models.Activity.stage.project == project_pk).where(
                models.Activity.stage == stage_pk)
        return_array = []
        for activity in activitys:
            return_array.append(model_to_dict(activity))
        return {'activities': json.dumps(return_array)}

    def post(self, project_pk, stage_pk):
        '''
            # XTRA - /project/{project_pk}/stages/- POST
            Though this wasn't requested, I propose posting new data here is
            the best way to make a new stage.
        '''
        activity = models.Activity.create(
            stage=stage_pk,
            name=request.form['name'],
            description=request.form['description']
        )
        return {'activity': model_to_dict(activity)}, 201


api.add_resource(
    Activities, '/projects/<project_pk>/stages/<stage_pk>/activities/')


class Activity(Resource):
    '''
        # /projects/{project_pk}/stages/{stage_pk}/activities/{pk}
            - GET, PUT, POST, DELETE
    '''

    def get(self, project_pk, stage_pk, pk):
        try:
            with models.DATABASE.atomic():
                project = models.Project.get(project_pk)
                stage = models.Stage.get(stage_pk)
                activity = models.Activity.get(pk)
            return {
                'project': model_to_dict(project),
                'stage': model_to_dict(stage),
                'activity': model_to_dict(activity)
            }
        except DoesNotExist:
            abort(404)

    def put(self, project_pk, stage_pk, pk):
        '''
            put is idempotent,
            calling it multiple times produces the same result
        '''
        with models.DATABASE.atomic():
            project = models.Project.get(project_pk)
            stage = models.Stage.get(stage_pk)
            activity = models.Activity.get(pk)
        if request.form['name']:
            activity.name = request.form['name']
        if request.form['description']:
            activity.description = request.form['description']
        activity.save()
        return {'activity': model_to_dict(activity)}, 202

    def post(self, project_pk, stage_pk, pk):
        '''
            There is no child element, so post just updates now
        '''
        activity = models.Activity.get(pk)

        if request.form['name']:
            activity.name = request.form['name']
        if request.form['description']:
            activity.description = request.form['description']
        activity.save()

        return model_to_dict(activity), 201

    def delete(self, project_pk, stage_pk, pk):
        try:
            with models.DATABASE.atomic():
                project = models.Project.get(project_pk)
                stage = models.Stage.get(stage_pk)
                activity = models.Activity.get(pk)
        except DoesNotExist:
            return abort(404)
        if stage.project == project_pk and activity.stage == stage_pk:
            activity.delete_instance(recursive=True)
            return '', 204
        return 'Primary keys not match.', 403


api.add_resource(
    Activity, '/projects/<project_pk>/stages/<stage_pk>/activities/<pk>')


if __name__ == '__main__':
    models.initialize()
    if DEBUG:
        app.run(debug=DEBUG, host=HOST, port=PORT)
    # TODO: make an else for running in prod
