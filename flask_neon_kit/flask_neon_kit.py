import os
import re
import inspect
import importlib
import json
import traceback

from .utils import string_to_bool
from .utils import to_dict

# Provides a CRUD System Integrated to Flask
class FlaskNeonKit(object):
    def __init__(self, app=None, db=None) -> None:
        self.app = None
        self.db = None

        if app:
            self.init_app(app)


    # Initialize the CRUD System with a Flask application, Flask request & database instances.
    def init_app(self, app, request, db):
        self.app = app
        self.app.flask_neon_sdk = self
        self.request = request
        self.db = db

        app_configs = self._load_config()

        abs_path = os.path.abspath((inspect.stack()[1])[1])
        project_root = os.path.dirname(abs_path)
        project_root = project_root.replace("\\", ("/"))
        project_root = project_root.split("/")[-1]

        # -------------------------------------------------------------------------------
        
        root_url = app_configs.get("root_url")
        models = self.get_models(project_root=project_root, models_directory=app_configs["models_directory"])

        root_url = app_configs.get("root_url")

        for model in models:
            app.route(f"{root_url}{model['model_url_prefix']}/{model.get('route_model_name')}", methods=["GET", "POST"])(self.db_interface(
                self.request,
                self.db,
                model.get('route_model_name'),
                model.get("model_class"),
                id=None
            ))
            app.route(f"{root_url}{model['model_url_prefix']}/{model.get('route_model_name')}/<id>", methods=["GET", "PUT", "PATCH", "DELETE"])(self.db_interface(
                self.request,
                self.db,
                model.get('route_model_name'),
                model.get("model_class"),
                id
            ))


    # Load the configurations from the Flask configuration
    def _load_config(self):
        options = dict()

        models_directory = self.app.config.get("MODELS_DIRECTORY")
        if models_directory:
            options["models_directory"] = models_directory
        else:
            options["models_directory"] = "models"

        url_prefix = self.app.config.get("URL_PREFIX")
        if url_prefix:
            options["url_prefix"] = url_prefix

        # ROOT URL
        root_url = self.app.config.get("ROOT_URL")
        if root_url:
            options["root_url"] = root_url
        else:
            options["root_url"] = ""


        return options
    

    # GET MODELS
    def get_models(self, project_root, models_directory):
        package_name = models_directory

        files = os.listdir(package_name)

        models = list()

        for file in files:
            if file not in ["__init__.py", "__pycache__"]:
                if file[-3:] != ".py":
                    continue

                file_name = file[:-3]

                module_name = ".." + package_name + "." + file_name
                
                for name, cls, in inspect.getmembers(importlib.import_module(module_name, package=f"{project_root}.{models_directory}"), inspect.isclass):
                    split = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split()

                    route_model_name = split[0].lower()
                    db_model_name = split[0].lower()

                    x = 1

                    if len(split) > 1:
                        while x < len(split):
                            route_model_name = route_model_name + f"-{split[x].lower()}"
                            db_model_name = db_model_name + f"_{split[x].lower()}"
                            x = x + 1
                    
                    # Check if there is Model URL Prefix
                    model_url_prefix = ""
                    if hasattr(cls, "model_url_prefix"):
                        model_url_prefix = cls.model_url_prefix

                    # Check if there is Custom Collection Name
                    custom_name = None
                    if hasattr(cls, "__tablename__"):
                        custom_name = cls.__tablename__

                    else:
                        custom_name = db_model_name

                    
                    models.append({
                        "model_url_prefix": model_url_prefix,
                        "route_model_name": route_model_name,
                        "table_name": custom_name,
                        "model_class": cls,
                    })

        return models

    # DB INTERFACE
    def db_interface(self, request, db, route_model_name, model_class, id):
        if id == None:
            def _dynamic_function():
                if request.method == "POST":
                    response = dict()
                    
                    try:
                        entity = request.json

                        model_attributes_list = list(inspect.signature(model_class).parameters)

                        new_enity = dict()

                        for z in model_attributes_list:
                            new_enity[z] = entity.get(z)

                        # Add Data to DB
                        new_object = model_class(**new_enity)
                        db.session.add(new_object)
                        db.session.commit()

                        new_object = to_dict(new_object)

                        response["message"] = f"{route_model_name} created successfully"
                        response["data"] = new_object

                    except:
                        response["message"] = f"failed to create {route_model_name}"
                        response["data"] = {}
                    
                    return response
                
                if request.method == "GET":
                    has_pagination = string_to_bool(request.args.get('pagination'))
                    page = request.args.get("page")
                    limit = request.args.get("limit")

                    has_next = None
                    has_prev = None
                    total = None

                    response = dict()

                    try:
                        if has_pagination:
                            if page is None and limit is None:
                                page = 1
                                limit = 5

                            elif page is None and limit:
                                page = 1

                            elif limit is None and page:
                                limit = 5
                            
                            entities = model_class.query.paginate(page=int(page), per_page=int(limit), error_out=False)
                            has_next = entities.has_next
                            has_prev = entities.has_prev
                            total = entities.total
                        else:
                            page = None
                            entities =  model_class.query.all()

                        if entities:
                            entities = [to_dict(entity) for entity in entities]

                        else:
                            entities = list()
                        
                        response["message"] = f"{route_model_name} retrieved successfully"

                    except:
                        traceback.print_exc()
                        entities = list()
                        response["message"] = f"failed to retrieve {route_model_name}"

                    response["data"] = entities
                    response["count"] = len(entities)
                    response["current_page"] = page
                    response["has_pagination"] = has_pagination
                    response["has_prev"] = has_prev
                    response["has_next"] = has_next
                    response["total"] = total
                    response["limit"] = limit

                    return response
                
            _dynamic_function.__name__ = route_model_name

            return _dynamic_function
        
        else:
            def _dynamic_function(id):

                if request.method == "GET":
                    response = dict()
                    entity = dict()

                    try:
                        entity =  model_class.query.filter_by(id=id).first()

                        if entity:
                            entity = to_dict(entity)
                            response["message"] = f"{route_model_name} retrieved successfully"

                        else:
                            entity = dict()
                            response["message"] = f"{route_model_name} not found"

                    except:
                        traceback.print_exc()
                        entity = dict()
                        response["message"] = f"failed to retrieve {route_model_name}"
                    
                    response["data"] = entity
                    return response
                
                if request.method == "PUT":
                    response = dict()
                    entity = dict()

                    new_entity = request.json

                    try:
                        entity = model_class.query.filter_by(id=id).first()

                        if entity:
                            for key, value in new_entity.items():
                                setattr(entity, key, value)

                            db.session.commit()
                            entity = to_dict(entity)

                            response["message"] = f"{route_model_name} updated successfully"

                        else:
                            entity = dict()
                            response["message"] = f"{route_model_name} not found"

                    except:
                        traceback.print_exc()
                        entity = dict()
                        response["message"] = f"failed to update {route_model_name}"

                    response["data"] = entity
                    return response
                
                if request.method == "DELETE":
                    response = dict()
                    entity = dict()

                    try:
                        entity =  model_class.query.filter_by(id=id).first()

                        if entity:
                            db.session.delete(entity)
                            db.session.commit()
                            entity = to_dict(entity)

                            response["message"] = f"{route_model_name} deleted successfully"

                        else:
                            entity = dict()
                            response["message"] = f"{route_model_name} not found"

                    except:
                        traceback.print_exc()
                        entity = dict()
                        response["message"] = f"failed to delete {route_model_name}"

                    response["data"] = entity
                    return response
            
            _dynamic_function.__name__ = route_model_name + "-one"

            return _dynamic_function