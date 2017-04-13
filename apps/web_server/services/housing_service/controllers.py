from flask import request, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import Pagination
from flask_restful import Resource, fields, marshal_with
from flask_security import current_user
from apps.api_server import api
from apps.api_server.services.housing_service.form import SearchForm, ReservationForm, EnquiryForm
from apps.api_server.services.housing_service.models import MainLocations, Housing, SearchLocations, Room, RoomImage, \
    HousingImage
from apps.web_server.services.housing_service import housing_blueprint
from apps.api_server.services.housing_service.utils import add_housing_reservation, add_housing_enquire
from apps import db


@housing_blueprint.route('/main')
def housing_main():
    # print(MainLocations.query.all())
    # print(MainLocations.query.get(1))
    main = MainLocations.query.filter().all()
    form = SearchForm(request.form)
    return render_template('housing/housing_main.html', main=main, form=form)


@housing_blueprint.route('/maps/<int:aa>')
def housing_map(aa):
    # print(MainLocations.query.all())
    # print(MainLocations.query.get(1))
    hm = MainLocations.query.get(aa)
    print(hm.get_main_location_latlong())
    hh = hm.get_main_location_latlong()
    housing = Housing.query.all()

    form = SearchForm(request.form)

    return render_template('map.html', hh=hh, housing=housing, form=form)


@housing_blueprint.route('/list/<float:sw_x>/<float:sw_y>/<float:ne_x>/<float:ne_y>')
def housing_list(sw_x, sw_y, ne_x, ne_y):
    search = False

    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get('page', type=int, default=1)

    housing = Housing.query.filter(Housing.latitude > sw_x, Housing.latitude < ne_x,
                                   Housing.longitude > sw_y, Housing.longitude < ne_y).all()

    pagination = Pagination(page=page, total=housing.count(), search=search, record_name='users')

    return render_template('housing/housing_list.html', housing=housing, pagination=pagination)


@housing_blueprint.route('/search', methods=['GET', 'POST'])
def housing_search():
    aa = 2
    form = SearchForm(request.form)
    keyword = ''

    if request.method == 'POST' and form.validate():
        keyword = form.keyword.data
        print(keyword)

    hh = SearchLocations.query.filter(SearchLocations.name.like("%" + keyword + "%")).first()
    print("----")
    print(hh)
    housing = Housing.query.all()
    if True:
        return render_template('map.html', hh=hh, housing=housing, form=form)
    else:
        return render_template('map.html', hh=hh, housing=housing, form=form)


housinglist_fields = {

    'id': fields.Integer,
    'name': fields.String,
    'address1': fields.String,
    'address2': fields.String,
    'description': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'lowest_price': fields.String(attribute='get_lowest_price'),
    'thumbnail_image': fields.String(attribute='get_thumbnail_image')
    # 'price': fields.Nested(nested='',attribute=)
}
house_list_fields = {
    'count': fields.Integer,
    'house': fields.Nested(housinglist_fields)
}


class Marker(Resource):
    @marshal_with(housinglist_fields, envelope="result")
    def get(self):
        # print("dddd")
        # print(request.environ)
        # for env in request.environ:
        #     print(env, ": ", request.environ[env])
        # print(request.args)
        sw_x = request.args.get('sw_x')
        sw_y = request.args.get('sw_y')
        ne_x = request.args.get('ne_x')
        ne_y = request.args.get('ne_y')

        print(sw_x)
        print(sw_y)
        print(ne_x)
        print(ne_y)
        if not (sw_x and sw_y and ne_x and ne_y):
            housing = Housing.query.all()

        else:

            search = False

            q = request.args.get('q')
            if q:
                search = True

            page = request.args.get('page', type=int, default=1)

            housing = Housing.query.filter(Housing.latitude > sw_x, Housing.latitude < ne_x,
                                           Housing.longitude > sw_y, Housing.longitude < ne_y).order_by(
                Housing.name).all()


            # print(housing)
            # print(housing.paginate(page=page, per_page=5).items)
            # print(housing.all())

            # pagination = Pagination(page=page, total=housing.count(), search=search, record_name='users')

        return housing


api.add_resource(Marker, '/marker')


class Arrange(Resource):
    @marshal_with(housinglist_fields, envelope="result")
    def get(self):

        num = request.args.get('num')
        sw_x = request.args.get('sw_x')
        sw_y = request.args.get('sw_y')
        ne_x = request.args.get('ne_x')
        ne_y = request.args.get('ne_y')
        lat = request.args.get('lat')
        lng = request.args.get('lng')

        lat = float(lat)
        lng = float(lng)

        print("temp", type(lat))
        print(lng)

        if num == "1":
            print("its 1")
            list = Housing.query.filter(Housing.latitude > sw_x, Housing.latitude < ne_x,
                                        Housing.longitude > sw_y,
                                        Housing.longitude < ne_y).order_by(Housing.name).all()
        elif num == "2":
            print("its 2")
            list = Housing.query.filter(Housing.latitude > sw_x, Housing.latitude < ne_x,
                                        Housing.longitude > sw_y,
                                        Housing.longitude < ne_y).order_by(Housing.get_lowest_price).all()
        elif num == "3":
            print("its 3")
            # list = Housing.query.filter(Housing.latitude > sw_x, Housing.latitude < ne_x,
            #                             Housing.longitude > sw_y,
            #                             Housing.longitude < ne_y).order_by(Housing.get_closest_distance(center_lng=lng,center_lat=lat))

            print(Housing.housing_detail(Housing))




            # list = Housing.query.filter(Housing.latitude > sw_x, Housing.latitude < ne_x,
            #                             Housing.longitude > sw_y,
            #                             Housing.longitude < ne_y).order_by(Housing.get_closest_distance).all()
            #
            # R = 6371
            # x = (list.longitude - lng) * cos(0.5* (list.latitude+lat))
            # print("x")
            # print(x)
            # y = Housing.latitude - lat
            # print("y")
            # print(y)
            # d = R * sqrt( x*x + y*y )
            #
            # print(d)
            # list = Housing.query.filter((Housing.longitude - lng)* cos(0.5* (Housing.latitude+lat)), Housing.latitude < ne_x,
            #                             Housing.longitude > sw_y,
            #                             Housing.longitude < ne_y).order_by(Housing.get_lowest_price).all()
            #
            #

        else:
            print("else")
            list = Housing.query.all()

        return list


api.add_resource(Arrange, '/arrange')


@housing_blueprint.route('/detail/<int:num>')
def housing_detail(num):
    print("number for detail")
    print(num)
    # print(MainLocations.query.all())
    # print(MainLocations.query.get(1))
    main = Housing.query.filter(Housing.id == num).first()
    room = Room.query.filter(Room.housing_service_id == num).all()

    housing = db.session.query(Housing, HousingImage).filter(Housing.id == HousingImage.housing_id).filter(
        Housing.id == num).all()
    form = SearchForm(request.form)

    return render_template('housing/housing_detail.html', form=form, main=main, room=room, housing=housing)


@housing_blueprint.route('/housing_reserve', methods=['POST'])
def housing_reserve():
    r_form = ReservationForm(request.form)
    form = request.form
    room_check = form['room_check']
    room = Room.query.filter(Room.id == room_check).first()
    main = Housing.query.filter(Housing.id == room.housingservice.id).first()
    session['reserve_room_no'] = room.id

    return render_template('housing/housing_reserve.html', r_form=r_form, room=room, main=main)


@housing_blueprint.route('/housing_enquire', methods=['POST'])
def housing_enquire():
    r_form = EnquiryForm(request.form)
    form = request.form
    print(form)
    room_check = form['room_check']
    room = Room.query.filter(Room.id == room_check).first()
    main = Housing.query.filter(Housing.id == room.housingservice.id).first()
    session['reserve_room_no'] = room.id
    print(room_check)

    return render_template('housing/housing_enquire.html', r_form=r_form, room=r_form, main=main)


@housing_blueprint.route('/housing_reserve_finish', methods=['POST'])
def housing_reserve_finish():
    r_form = ReservationForm(request.form)
    room_id = session.get('reserve_room_no')

    room = Room.query.filter(Room.id == room_id).first()

    main = Housing.query.filter(Housing.id == room.housingservice.id).first()

    if not r_form.validate():
        print('All fields are required.')
        return render_template('housing/housing_reserve.html', r_form=r_form, room=room, main=main)
    elif r_form.validate():
        add_housing_reservation(room.housingservice.id, current_user.id, request.form['user_name'],
                                request.form['email'],
                                request.form['checkin_date'], request.form['checkout_date'], request.form['comments'],
                                request.form['nationality'],
                                request.form['kakao_id'],
                                request.form['mobile_no'])
        reserve_room_no = session.get('reserve_room_no')
        if not reserve_room_no:
            return "세션이 만료되었습니다"
        session.pop('reserve_room_no')
        print("4")
        return redirect(url_for('housing.housing_detail', num=reserve_room_no))


@housing_blueprint.route('/housing_enquire_finish', methods=['POST'])
def housing_enquire_finish():
    r_form = EnquiryForm(request.form)
    room_id = session.get('reserve_room_no')

    room = Room.query.filter(Room.id == room_id).first()

    main = Housing.query.filter(Housing.id == room.housingservice.id).first()

    if not r_form.validate():
        print('All fields are required.')
        return render_template('housing/housing_enquire.html', r_form=r_form, room=room, main=main)
    elif r_form.validate():
        add_housing_enquire(room.housingservice.id, current_user.id, request.form['user_name'], request.form['email'],
                            request.form['enquiry'],
                            request.form['nationality'],
                            request.form['kakao_id'],
                            request.form['mobile_no'])
        reserve_room_no = session.get('reserve_room_no')
        if not reserve_room_no:
            return "세션이 만료되었습니다"
        session.pop('reserve_room_no')
        print("4")
        return redirect(url_for('housing.housing_detail', num=reserve_room_no))
