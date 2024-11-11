import os

#from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy  # If you don't already have SQLAlchemy imported


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Configure db
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/finance")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Gets a ditionary of the stocks that the curent user has purchased
    stocks=db.execute("SELECT symbol, SUM(shares) FROM purchases WHERE user_id=? GROUP BY symbol", session['user_id'])


    # Finds the current price of each one
    for stock in stocks:
        #stock['price']=lookup(stock['symbol'])['price']
        stock_data = lookup(stock['symbol'])
        if stock_data is None:
            # Handle the case where lookup fails, perhaps set a default price or show an error
            stock['price'] = "N/A"  # or any placeholder value
        else:
            stock['price'] = stock_data['price']

    # If the dictionary isn't empty, renders the index template and passses it the dictionary
    if(stocks):
        return render_template("index.html", stocks=stocks)

    else:
        return apology("no stocks to show",200)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # If accessed via a url
    if request.method =="GET":
        return render_template("buy.html")

    # If the form in buy.html is submitted
    else:
        # Gets symbol and returns apology if it doesn't exist or it's invalid
        symbol=request.form.get("symbol")
        if (not symbol or lookup(symbol)==None):
            return apology("please enter valid symbol")

        # Gets shares and returns apology if it doesn't exist or it's not an integer
        shares=request.form.get("shares")
        if (not shares or not shares.isdigit()):
            return apology("please enter valid number of shares")

        # Finds the price of the stock and the ammount of money that the user has
        price=lookup(symbol)['price']
        cash=db.execute("SELECT cash  FROM users WHERE id = ?",session['user_id'])[0]['cash']

        # Checks if the user can afford their purchase
        if (int(price)*int(shares) > cash):
            return apology("not enough money in account")

        # Inserts the data - the user_id, the symbol, the number of shares and the price at the time, as well as a timestamp,  for the new purchase into a purchases table
        else:
            db.execute("CREATE TABLE IF NOT EXISTS purchases(user_id INTEGER NOT NULL,symbol TEXT NOT NULL, price NUMERIC NOT NULL,shares NUMERIC NOT NULL,timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))")
            db.execute("INSERT INTO purchases(user_id, symbol, price, shares) VALUES(?,?,?,?)", session['user_id'],symbol,price,shares)
        return redirect("/")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # If accessed via url
    if request.method =="GET":
        return render_template("quote.html")

    # If the formin quote.html is submitted
    else:
        # Gets the symbol and checks if it's valid
        symbol = request.form.get("symbol")
        if not symbol or not lookup(symbol):
            return apology("please enter valid symbol")
        # Returns the price and the symbol that was searched
        else:
            return render_template("quote_lookup.html", symbol=lookup(symbol))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # When the form is submitted
    if request.method=="POST":

        # Gets username and checks if it's blank
        username=request.form.get("username")
        if not username:
            return apology("please input username",400)

        # Gets password and checks if it's blank
        password=request.form.get("password")
        if not password:
            return apology("please input password",400)

        # Gets confirmation and checks if it's blank
        confirmation=request.form.get("confirmation")
        if not confirmation:
            return apology("please confirm password",400)


        # Checks if the password and confirmation match
        if (password==confirmation):
            # Tries to insert the user's data into the database
            try:
                db.execute("INSERT INTO users(username,hash) VALUES(?,?)", username, generate_password_hash(password, method='pbkdf2', salt_length=16))
            # If the username is a duplicate the sql query is unable to execute because of the UNIQUE INDEX on username
            except ValueError:
                return apology("username already exists",400)
        else:
            return apology("password and confirmation do not match", 400)

        return redirect("/")

    # When accessed via url
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
