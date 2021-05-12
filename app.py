from flask import Flask
from flask_restful import Api, Resource
from flask_restful import reqparse
from flask_restful import inputs
import datetime as dt
from datetime import datetime as dtdt
from flask_sqlalchemy import SQLAlchemy
from flask import abort
import sys

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser_time = reqparse.RequestParser()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ToDoList.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# write your code here
parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)
parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)
parser_time.add_argument(
    'start_time',
    type=inputs.date,
    help='input start time',
    required=False
)
parser_time.add_argument(
    'end_time',
    type=inputs.date,
    help='input end time',
    required=False
)



class ToDoList(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    event = db.Column(db.String(100), nullable = False)
    date = db.Column(db.Date, nullable = False)

    def __repr__(self):
        return f"{self.id}|{self.event}|{self.date}"


db.create_all()

def small_converter(cntx_list):
    all_args = list()
    for cntx in cntx_list:
        event_id = str(cntx).split(sep='|')[0]
        event = str(cntx).split(sep='|')[1]
        date = str(cntx).split(sep='|')[2]
        all_args.append({'id': event_id, 'event': event, 'date': date})
    return all_args


class EventEndPoint(Resource):
    def get(self):
        time_args = parser_time.parse_args()
        if time_args['start_time'] or time_args['end_time'] is not None:
            if time_args['end_time'] is None:
                return {"message": "end_time is missing'"}
            elif time_args['start_time'] is None:
                return {"message": "start_time is missing'"}
            else:
                zoned_event = ToDoList.query.filter(ToDoList.date.between(time_args['start_time'],time_args['end_time'])).all()
                if len(zoned_event) == 0:
                    return small_converter(ToDoList.query.all())
                return small_converter(ToDoList.query.filter(ToDoList.date.between(time_args['start_time'],time_args['end_time'])).all())
        else:
            return small_converter(ToDoList.query.all())

    def post(self):
        args = parser.parse_args()
        args['date'] = args['date'].strftime('%Y-%m-%d')
        if 'date' and 'event' in args:
            args.update({'message':'The event has been added!'})
            args['date'] = dtdt.strptime(args['date'], '%Y-%m-%d')
            args_to_db = ToDoList(date=args['date'], event=args['event'])
            db.session.add(args_to_db)
            db.session.commit()
        args['date'] = args['date'].strftime('%Y-%m-%d')
        return args


class EventTodayEndPoint(Resource):
    def get(self):
        return small_converter(ToDoList.query.filter(ToDoList.date == dt.date.today()).all())


class EventByID(Resource):
    def get(self, event_id):
        event = ToDoList.query.filter(ToDoList.id == event_id).first()
        if event is None:
            abort(404,"The event doesn't exist!")
        event_id = str(event).split(sep='|')[0]
        eventq = str(event).split(sep='|')[1]
        date = str(event).split(sep='|')[2]
        return {'id': event_id, 'event': eventq, 'date': date}

    def delete(self, event_id):
        event = ToDoList.query.filter(ToDoList.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        db.session.delete(event)
        db.session.commit()
        return {"message": "The event has been deleted!"}


api.add_resource(EventEndPoint, '/event')
api.add_resource(EventTodayEndPoint, '/event/today')
api.add_resource(EventByID, "/event/<int:event_id>")

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
