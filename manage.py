import sys
from flask_script import Manager, Command
from flask_script.commands import InvalidCommand
from apps import app, db
from flask_migrate import Migrate, MigrateCommand

# 개발서버
# migrate = Migrate(app, db)

# 제품 서버
migrate = Migrate(app, db, 'product_migrations')

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from apps.api_server.address.models import Country, CountrySubdivision


@manager.command
def populate_country(*args, **options):
    try:
        import pycountry
    except ImportError:
        raise InvalidCommand(
                "You are missing the pycountry library. Install it with "
                "'pip install pycountry'")

    if Country.query.all():
        if options.get('is_initial_only', False):
            print("Countries already populated; nothing to be done.")
            sys.exit(0)
        else:
            raise InvalidCommand(
                    "You already have countries in your database. "
                    "This command currently does not support updating existing countries.")

    countries = [
        Country(iso_3166_1_a2=country.alpha2,
                iso_3166_1_a3=country.alpha3,
                iso_3166_1_numeric=country.numeric,
                printable_name=country.name,
                name=getattr(country, 'official_name', ''))
        for country in pycountry.countries]

    db.session.add_all(countries)
    db.session.commit()
    print("Successfully added %s countries." % len(countries))

@manager.command
def populate_subdivision(*args, **options):
    try:
        import pycountry
    except ImportError:
        raise InvalidCommand(
                "You are missing the pycountry library. Install it with "
                "'pip install pycountry'")

    # Country가 없으면 에러
    if not Country.query.all():
        if options.get('is_initial_only', False):
            print("Countries already populated; nothing to be done.")
            sys.exit(0)
        else:
            raise InvalidCommand(
                    "You already have countries in your database. "
                    "This command currently does not support updating existing countries.")

    if CountrySubdivision.query.all():
        if options.get('is_initial_only', False):
            print("Subdivision already populated; nothing to be done.")
            sys.exit(0)
        else:
            raise InvalidCommand(
                    "You already have subdivision in your database. "
                    "This command currently does not support updating existing subdivision.")
    count=0
    for division in pycountry.subdivisions:
        try:
            country = Country.query.get(division.country.alpha2)
        except KeyError as e:
            print('에러발생')
            continue

        subdivision = CountrySubdivision(
            code=division.code,
            type=division.type,
            name=division.name,
            country=country,
            parent_code=division.parent_code
        )

        db.session.add(subdivision)
        count = count+1

    db.session.commit()
    print("완료" + str(count))


    # db.session.add_all(subdivisions)
    # db.session.commit()
    # db.session.rollback()


if __name__ == '__main__':
    manager.run()
