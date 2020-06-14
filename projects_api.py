from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
import os.path
import datetime

app = Flask(__name__)
app.debug = True

api = Api(app)
db = SQLAlchemy(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'projects_db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    info = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, name, url, info):
        self.name = name
        self.url = url
        self.info = info

    def _format_date(self, datetime: datetime.datetime):
        return datetime.strftime('%d.%m.%Y %H:%M')

    @property
    def __details(self):
        return f'<<{self.id}>> {self.name}, url: {self.url}, details: {self.info}, ' \
               f'created on: {self._format_date(self.created_on)}'

    def __str__(self):
        return self.__details

    def __repr__(self):
        return self.__details

    def _json(self):
        fields = {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "info": self.info,
            "created_on": self._format_date(self.created_on),
            "updated_on": self._format_date(self.updated_on)
        }
        return fields


class Actions(Resource):

    def _get_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('url')
        parser.add_argument('info')
        params = parser.parse_args()
        return params

    def _get_404(self, id):
        return f'Could not find project with id: {id}', 404

    def get(self, id=None):
        if id is None:
            projects = db.session.query(Project).all()
            result = [project._json() for project in projects]
            return result, 200

        project = db.session.query(Project).get(id)
        if project:
            return project._json(), 200
        return self._get_404(id)

    def post(self):
        params = self._get_params()
        new_project = Project(
            params['name'],
            params['url'],
            params['info'],
        )

        db.session.add(new_project)
        db.session.commit()
        return new_project._json(), 201

    def put(self, id):
        project = db.session.query(Project).get(id)
        if not project:
            return self._get_404(id)

        params = self._get_params()
        project.name = params['name']
        project.url = params['url']
        project.info = params['info']

        db.session.commit()
        return project._json(), 200

    def delete(self, id):
        project = db.session.query(Project).get(id)
        if not project:
            return self._get_404(id)

        db.session.delete(project)
        db.session.commit()
        return f'Project with id {id} has been deleted', 200


def main():
    api.add_resource(Actions, '/project/', '/project/<int:id>')
    app.run()


if __name__ == '__main__':
    main()
