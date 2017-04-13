
(extract - 추출하기): pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

(init - 없는 langs만들기): pybabel init -i messages.pot -d translations -l <문자코드>

(update - 기존것과 merge ): pybabel update -i messages.pot -d translations

(컴파일 - po를 mo로): pybabel compile -d translations

