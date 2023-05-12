from flask import Flask
from flask import request, redirect, render_template, url_for, send_from_directory

app = Flask(__name__)

#  Упрощенная версия сайта: https://fincult.info/calc/loan/#amount


@app.route('/', methods=['post', 'get'])
def index():
    # Сумма кредита
    sum = 1000
    # Процент по кредиту
    procent = 5
    # Срок кредита
    term = 10

    # Порядок погашения:
    # При аннуитетном погашении размер ежемесячного платежа остается одинаковым в течение всего срока кредита.
    # Однако сначала заемщик гасит в основном проценты и только со второй половины срока начинает уменьшать сумму основного долга.
    # При дифференцированном способе расчета заемщик каждый месяц вносит фиксированную сумму в счет погашения основного долга плюс сверх нее оплачивает проценты.
    # Благодаря тому, что проценты всегда рассчитываются исходя из оставшейся суммы долга,
    # процентная часть платежа со временем начинает уменьшаться — а вслед за ней уменьшается и весь размер ежемесячного взноса.
    is_annuity = False  # else it is differential

    # Берем данные
    for p in request.form:
        if p == 'sum':
            sum = int(request.form[p])
        if p == 'procent':
            procent = float(request.form[p])
        if p == 'term':
            term = int(request.form[p])
        if p == 'is_annuity':
            is_annuity = request.form[p]

    # Записываем данные в массив, чтобы передать его в render_template
    params = {'sum': sum, 'procent': procent, 'term': term, 'is_annuity': is_annuity}
    # Возвращает шаблон. payment_schedule - передаваемый график платежей.
    # Метод answer считает график платежей.
    return render_template('index.html', payment_schedule=answer(sum, procent, term, is_annuity), params=params)


#Считает график платежей. Получает на вход все данные о кредите
def answer(sum, procent, term, is_annuity):
    # Ответ -- график выплат
    result = {'Месяц': [], 'Платеж': [], 'Остаток': [], 'Переплата': 0, 'Всего выплат': 0,}
    # Остаток -- сумма, которую осталось выплатить выплатить
    ostatok = sum
    # Реально выплаченная сумма
    real_sum = 0
    # Пересчитываем процент с годового на месячный
    procent = procent / (100 * 12)

    # Если платеж аннуитетный
    if is_annuity:
        # Формула расчета взята из интернета
        loan_payment = sum * (procent * (1 + procent) ** term) / ((1 + procent) ** term - 1)

        for i in range(term):
            # Добавляем новый месяц
            result['Месяц'].append(i + 1)
            # Если рассчитанный платеж больше оставшейся суммы, требуемой для выплаты, выплачиваем остаток
            if i != 0 and loan_payment > ostatok:
                result['Платеж'].append(round(ostatok,3))
                real_sum += ostatok
            # Иначе добавляем в Платежи посчитанный платеж,
            else:
                result['Платеж'].append(round(loan_payment,3))
                real_sum += loan_payment

            old_ostatok = ostatok
            # Добавляем к требуемой сумме проценты по кредиту
            ostatok = ostatok * (1 + procent) - loan_payment

            # Если остаток получился отрицательным, записываем ноль
            if ostatok < 0:
                result['Остаток'].append(0)
            else:
                result['Остаток'].append(round(ostatok,3))

        # Переплатой является разность между реально выплаченными деньгами и взятым кредитом
        result['Всего выплат'] = round(real_sum, 3)
        result['Переплата'] = round(real_sum - sum, 3)

        return result

    else:
        # ДП = ОЗ / КП + ОЗхМС.
        # Где
        # ОЗ – остаток задолженности,
        # КП – количество
        # месяцев до погашения
        # долга, МС – месячная
        # ставка(поделить кредитную ставку на 12)

        for i in range(term):

            # Добавляем новый месяц
            result['Месяц'].append(i + 1)

            loan_payment = ostatok / (term - i) + ostatok * procent

            # Если рассчитанный платеж больше оставшейся суммы, требуемой для выплаты, выплачиваем остаток
            if i > 0 and loan_payment > result['Остаток'][i - 1]:
                result['Платеж'].append(round(ostatok,3))
                real_sum += ostatok

            # Иначе добавляем в Платежи посчитанный платеж,
            else:
                result['Платеж'].append(round(loan_payment,3))
                real_sum += loan_payment

            # Добавляем к требуемой сумме проценты по кредиту
            ostatok = ostatok * (1 + procent) - loan_payment

            # Если остаток получился отрицательным, записываем ноль
            if ostatok < 0:
                result['Остаток'].append(0)
            else:
                result['Остаток'].append(round(ostatok,3))

        result['Всего выплат'] = round(real_sum,3)
        result['Переплата'] = round(real_sum-sum,3)
        return result


if __name__ == '__main__':
    app.run(debug=True)
