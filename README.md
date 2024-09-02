# Flask Neon Kit Docs

## Features
- Automatically generates CRUD endpoints from defined model.
- Allows to customize app base URL as well as each model's url prefix.
- Allows to paginate when getting many entities from database table.

## Installation
```bash
pip install flask-neon-kit
```

## Configuration
- Empty __init__.py file required in project root directory.
- ROOT_URL can be configured in application's configurations and it is *optional*.
- If configured, it is used by all generated endpoints.
- Code snippet in **Basic Application** section shows how to configure ROOT_URL.
- Models:
    - Models directory is required in the project root directory:
    - If custom name Models directory is not defined, as:
        ~~~python
        app.config[MODELS_DIRECTORY] = "<CUSTOM_NAME>"
        ~~~
        - then, default “models” directory will be used.
        - This is where models files are defined.
        - Inside these files declare models classes and their configurations such as:
            - *model_url_prefix [OPTIONAL]*
            - and those supported by Flask SQLAlchemy
        - *model_url_prefix* allows to have unique URLs for each and every model.
        - If this configuration is not defined, default configuration will be used.
    - Model Class Code Snippet:
        ```python
        class ProfessorSubject:
            model_url_prefix = "/professor-subject-test"

            id = db.Column(db.Integer, primary_key=True, autoincrement=True)
            professor_first_name = db.Column(db.String())
            professor_last_name = db.Column(db.String())
            subject_name = db.Column(db.String())

            # These are entity fields
            def __init__(self, professor_first_name, professor_last_name, subject_name):
                self.professor_first_name = professor_first_name
                self.professor_last_name = professor_last_name
                self.subject_name = subject_name
        ```

## Basic Application
- Code Snippet:
    ```python
    from flask import Flask, request
    from .config import DbConfig
    from .database import db
    from flask_neon_kit import FlaskNeonKit

    app = Flask(__name__)
    # If models directory is not defined, default "models" directory will be used
    app.config["MODELS_DIRECTORY"] = "<CUSTOM_NAME>"
    # If root URL is not defined, generated endpoints will not have a root URL
    app.config["ROOT_URL"] = "/flask-neon-kit/v1"

    app.config.from_object(DbConfig)

    # Database related part
    db.init_app(app)
    # migrate = Migrate(app, db)

    flask_neon_kit = FlaskNeonKit()
    flask_neon.init_app(app, request, db)

    if __name__ == "__main__":
        app.run(debug=True)
    ```

## Generated Endpoints Examples and HTTP Methods:
- HTTP Methods supported are POST, GET, PUT and DELETE.
- The following generated endpoints will be using model snippet defined earlier in **Configuration** as well **Basic Application** sections.
- These endpoints are after application base URL:
    `<IP_ADDRESS>:<PORT_NUMBER>`
- Basic complete URL looks like:
    
    `<IP_ADDRESS>:<PORT_NUMBER>/<ROOT_URL>/<MODEL_URL_PREFIX>/<RESOURCE_NAME>`

    or

    `<IP_ADDRESS>:<PORT_NUMBER>/<ROOT_URL>/<MODEL_URL_PREFIX>/<RESOURCE_NAME>/<RESOURCE_IDENTIFIER>`
- RESOURCE_NAME is automatically generated, and a developer can not customize it.
- RESOURCE_IDENTIFIER should be the entity ID.
- Given the generated URL:
    `localhost:5000/flask-neon-kit/v1/professor-subject-test/professor-subject/2`:
    - "/professor-subject" is the RESOURCE_NAME.
    - "/2" is the RESOURCE_IDENTIFIER.
    - In case ROOT_URL is not specified:
        - In the above URL, ROOT_URL is `/flask-neon-kit/v1`.
        - The URL without ROOT_URL is `/professor-subject-test/professor-subject`
    - In case MODEL_URL_PREFIX is not specified:
        - In the above URL, MODEL_URL_PREFIX is `/professor-subject-test`
        - The URL without MODEL_URL_PREFIX is `/flask-neon-kit/v1/professor-subject`
    - In case both ROOT_URL and MODEL_URL_PREFIX are not specified:
        - The URL without both is `/professor-subject`
        - It contains only the RESOURCE_NAME.

#### POST
- Saves new entity into the database
- Only saves one entity at a time.
- Supports only JSON data.

- JSON Payload Example:
    ```json
    {
        "professor_first_name": "Foo",
        "professor_last_name": "Bar",
        "subject_name": "Comp Science"
    }
    ```

#### GET
- Retrieves entities from the database.
- Can retrieve only one entity or a list of entities.
- To retrieve only one entity, include RESOURCE_IDENTIFIER in the URL.
- This RESOURCE_IDENTIFIER will be used to identify that one entity.
- If RESOURCE_IDENTIFIER is not provided, list of entities will be retrieved.
- Developer can opt for pagination when retrieving many entities.
- To paginate, provide the following query parameters:
    - **pagination** = *true*. If "false", all entities will be retrieved from the database table.
    - **limit** = "number of entities" per page. Should be integer greater than 0. If not provided and pagination is true, default value of 5 will be used.
    - **page** = "page number". Should be integer greater than 0. If not provided and pagination is true, default value of 1 will be used.

#### PUT
- Updates one entity at a time.
- That entity is identified by RESOURCE_IDENTIFIER in the URL.
- If there is no such entity in the database, "<RESOURCE_NAME> not found" response will be returned.

#### DELETE
- Deletes one entity at a time.
- That entity is identified by RESOURCE_IDENTIFIER in the URL.
- If there is no such entity in the database, the endpoint will return a payload:
    ```json
    {
        "message": "<RESOURCE_NAME> not found"
    }
    ```