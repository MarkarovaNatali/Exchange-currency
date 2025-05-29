from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_URL = "https://api.nbrb.by/exrates/rates?periodicity=0"

@app.route("/", methods=["GET", "POST"])
def index():
    # Получаем данные с API
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()

    # Значения по умолчанию для конвертера
    amount = 100
    from_currency = "BYN"
    to_currency_1 = "EUR"
    to_currency_2 = "USD"
    converted_1 = None
    converted_2 = None

    if request.method == "POST":
        # Получаем данные из формы
        amount = float(request.form.get("amount", 1))
        from_currency = request.form.get("from_currency")
        to_currency_1 = request.form.get("to_currency_1")
        to_currency_2 = request.form.get("to_currency_2")

        # Формируем словарь с курсами и масштабами валют
        rates = {currency["Cur_Abbreviation"]:
                 [currency["Cur_OfficialRate"], currency["Cur_Scale"]]
                 for currency in data}
        # Добавляем BYN, так как его нет в API
        rates["BYN"] = [1, 1]

        if from_currency in rates:
            # Вычисление результатов конвертации:
            converted_1 = amount / (rates[from_currency][0] / rates[from_currency][1]) \
                          * (rates[to_currency_1][0] / rates[to_currency_1][1])
            converted_2 = amount / (rates[from_currency][0] / rates[from_currency][1]) \
                          * (rates[to_currency_2][0] / rates[to_currency_2][1])

    return render_template("index.html", data=data, amount=amount, from_currency=from_currency,
                           to_currency_1=to_currency_1, to_currency_2=to_currency_2,
                           converted_1=converted_1, converted_2=converted_2)


@app.route("/get_rate", methods=["GET", "POST"])
def get_rate():
    response = requests.get(API_URL)
    data = response.json()
    selected_currency = None
    rate = None
    scale = None
    currency_name = None

    if request.method == "POST":
        selected_currency = request.form.get("currency")
        for currency in data:
            if currency["Cur_Abbreviation"] == selected_currency:
                scale = currency["Cur_Scale"]
                currency_name = currency["Cur_Name"]
                rate = currency["Cur_OfficialRate"]
                break

    return render_template("index.html", data=data, selected_currency=selected_currency,
                           rate=rate, currency_name=currency_name, scale=scale)


@app.route("/update", methods=["POST", "GET"])
def update():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        data = []
        print(f"Ошибка загрузки данных: {e}")
    return render_template("index.html", data=data)


@app.route("/convert", methods=["GET", "POST"])
def convert():
    # Обработчик конвертера, где используется только официальная ставка (с масштабом)
    response = requests.get(API_URL)
    data = response.json()

    amount = 100
    from_currency = "BYN"
    to_currency_1 = "EUR"
    to_currency_2 = "RUB"
    converted_1 = None
    converted_2 = None

    if request.method == "POST":
        amount_input = request.form.get("amount", 1)
        if not amount_input:
            error_message = "Сумма для конвертации не была введена"
            return render_template("index.html", error=error_message, data=data)
        amount = float(amount_input)
        from_currency = request.form.get("from_currency")
        to_currency_1 = request.form.get("to_currency_1")
        to_currency_2 = request.form.get("to_currency_2")

        # Формируем словарь с курсами и масштабами валют
        rates = {currency["Cur_Abbreviation"]:[currency["Cur_OfficialRate"], currency["Cur_Scale"]]
                 for currency in data}
        rates["BYN"] = [1, 1]

        if from_currency in rates:
            converted_1 = amount / (rates[to_currency_1][0] / rates[to_currency_1][1]) \
                          * (rates[from_currency][0] / rates[from_currency][1])
            converted_2 = amount / (rates[to_currency_2][0] / rates[to_currency_2][1]) \
                          * (rates[from_currency][0] / rates[from_currency][1])

    return render_template("index.html", data=data, amount=amount, from_currency=from_currency,
                           to_currency_1=to_currency_1, to_currency_2=to_currency_2,
                           converted_1=converted_1, converted_2=converted_2)


if __name__ == "__main__":
    app.run(debug=False)
