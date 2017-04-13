from apps import app

CURRENCY = [('USD', 1), ('KRW', 1100)]


@app.template_filter('to_usd')
def trans_currency(price, from_currency='KRW', to_currency='USD'):
    try:
        price = float(price)
    except:
        raise ValueError('Float로 형 변환이 가능해야 합니다.')

    for cur in CURRENCY:
        if cur[0] == from_currency:
            from_price = cur[1]
        if cur[0] == to_currency:
            to_price = cur[1]

    # 환율 비율 계산
    result_price_per = to_price/from_price

    # 결과값 계산   가격 * 비율
    result_price = price *result_price_per

    # 소수점 3째자리 반올림
    result_price = round(result_price, 2)

    return (to_currency, result_price)



