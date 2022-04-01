from typing import List, Dict
from flask import Flask,render_template, Response
from flask import request, url_for, redirect, flash
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import json
import datetime
import io

app = Flask(__name__)
# app must contain a secret key
app.secret_key = "super secret key"


# get invitation data from database, stores in a list of dictionary
def get_invitation() -> List[Dict]:
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'immi',
        'auth_plugin': 'mysql_native_password'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM invitation Order by date')
    results = [{'date': str(date), 'category': category, 'amount': amount} for (date, category, amount) in cursor]
    cursor.close()
    connection.close()
    return results


# add distribution table and data into database
def add_distribution_table():
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'immi',
        'auth_plugin': 'mysql_native_password'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS `distribution` (
    `pool_date` DATE PRIMARY KEY,
    `601-1200` INT,
    `501-600` INT,
    `451-500` INT,
    `491-500` INT,
    `481-490` INT,
    `471-480` INT,
    `461-470` INT,
    `451-460` INT,
    `401-450` INT,
    `441-450` INT,
    `431-440` INT,
    `421-430` INT,
    `411-420` INT,
    `401-410` INT,
    `351-400` INT,
    `301-350` INT,
    `0-300` INT)""")
    cursor.execute("""insert ignore into distribution
    values ('2022-03-28',873,5563,47599,2989,6310,14759,13218,10323,47276,9736,10207,7633,9240,10460,58253,31018,5313)""")
    connection.commit()
    cursor.close()
    connection.close()


# get distribution data from database, stores in a list of dictionary
def get_distribution():
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'immi',
        'auth_plugin': 'mysql_native_password'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM distribution')
    results = [{'date': str(item[0]),
                '601-1200': item[1],
                '501-600': item[2],
                '451-500': item[3],
                '401-450': item[9],
                '351-400': item[15],
                '301-350': item[16],
                '0-300': item[17]} for item in cursor]
    cursor.close()
    connection.close()
    return results


# save bar plot as .png file under /bar-plot.png
@app.route('/bar-plot.png')
def plot_bar():
    fig = create_bar_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


# plot bar chart
def create_bar_figure():
    fig = Figure()
    # axis = fig.add_subplot(1, 1, 1)
    # xs = range(100)
    # ys = [random.randint(1, 50) for x in xs]
    # axis.plot(xs, ys)
    # make data:
    plt.switch_backend('agg')

    count=1
    left = []
    height = []
    tick_label = []
    result = get_invitation()
    for item in result:
        # left = [1, 2, 3, 4, 5]
        left.append(count)
        # heights of bars
        # height = [10, 24, 36, 40, 5]
        height.append(int(item['amount']))
        # labels for bars
        # tick_label = ['one', 'two', 'three', 'four', 'five']
        tick_label.append(item['date'])
        count += 1

    # plot
    fig, ax = plt.subplots()

    ax.bar(left, height, width=0.7, edgecolor="white", linewidth=0.7, align="center")

    ax.set(xlim=(0, len(left)+1), xticks=left,
           ylim=(0, max(height)+200), yticks=height)
    ax.set_title('IRCC Invitation trend')
    ax.set_xticklabels(tick_label)
    return fig


# save pie plot as .png file under /pie-plot.png
@app.route('/pie-plot.png')
def plot_pie():
    fig = create_pie_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


# plot pie chart
def create_pie_figure():
    fig1 = Figure()
    # switch to non-gui backend
    plt.switch_backend('agg')

    result = get_distribution()
    labels = '601-1200', '501-600', '451-500', '401-450', '351-400', '301-350', '0-300'
    # sizes = [15, 30, 45, 10]
    sizes = [int(result[0]['601-1200']), int(result[0]['501-600']), int(result[0]['451-500']),
             int(result[0]['401-450']), int(result[0]['351-400']), int(result[0]['301-350']),
             int(result[0]['0-300'])]
    explode = (0, 0, 0, 0, 0, 0, 0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode,
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    sum_sizes = sum(sizes)
    # label name and size in legend
    labels = [f'{l}, {s/sum_sizes*100:0.1f}%' for l, s in zip(labels, sizes)]
    ax1.legend(labels=labels,loc="upper left", bbox_to_anchor=(0.8, 1.1))
    ax1.set_title('IRCC Distribution on %s' % (result[0]['date']))
    return fig1


# check for date format
def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


# route for index page
@app.route('/', methods=['GET', 'POST'])
def index():
    add_distribution_table()
    return render_template('index.html', invitations=get_invitation())


# route for add invitation page
@app.route('/addinvitation', methods=['GET', 'POST'])
def add_invitation():
    if request.method == 'POST':  # check for POST request
        # get form data
        date = request.form.get('date')
        category = request.form.get('category')
        amount = request.form.get('amount')
        # Validate data
        if not date or not category or not amount or validate(date) is False:
            flash('Invalid input.')  # Display error
            return redirect(url_for('index'))  # redirect to index page
        # Save data to database
        config = {
            'user': 'root',
            'password': 'root',
            'host': 'db',
            'port': '3306',
            'database': 'immi',
            'auth_plugin': 'mysql_native_password'
        }
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        sql_statement = 'INSERT INTO invitation VALUES (%s, %s, %s)'
        try:
            cursor.execute(sql_statement, (date, category, amount))
        except mysql.connector.IntegrityError:
            flash('Duplicated date! Invalid input')
            cursor.close()
            connection.close()
            return redirect(url_for('index'))
        connection.commit()
        flash('Item created.')
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    return render_template('addinvitation.html')


# route for about the author page
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


# route for all the data in database
@app.route('/jsondump/')
def jsondump() -> str:
    add_distribution_table()
    return json.dumps({'invitations': get_invitation(),'distributions':get_distribution()})


# route for error handler page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# main function runs on port 80
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
