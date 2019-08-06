# Experiment with Flask

from flask import Flask, render_template, json, request, redirect
from flask import session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
# Set a secret for  user session ?
app.secret_key = "why would I tell you my secret key?"


# To connect with MySQL, we'll be using Flask-MySQL
mysql = MySQL()
# MySQL configurations
app.config["MYSQL_DATABASE_USER"] = "mapi"
app.config["MYSQL_DATABASE_PASSWORD"] = "mapi"
app.config["MYSQL_DATABASE_DB"] = "Muzapi"
app.config["MYSQL_DATABASE_HOST"] = "localhost"
mysql.init_app(app)


@app.route("/")
def main():
    """
    INFO:
          - app.route() is a 'view function' of Flask. View functions are mapped to one or more route URLs so that Flask knows what logic to execute when a client requests a given URL
          - Flask makes it possible to write "@app.route()" at the top of the function and expose its result to the internet.
          - more at https://ains.co/blog/things-which-arent-magic-flask-part-1.html
    """

    return render_template("index.html")


@app.route("/showSignUp")
def showSignUp():
    return render_template("signup.html")


@app.route("/signUp", methods=["POST"])
def signUp():
    """
    In order to read the posted values we need  to import request from Flask.
    Use jQuery AJAX to send the signup request to the Python method. We sort of send data to this method by using javascript.
    """
    # read the posted values from the UI. request() is Flask method that give access to fields in a filled in form.
    _name = request.form["inputName"]
    _email = request.form["inputEmail"]
    _password = request.form["inputPassword"]

    # Create the MySQL connection:
    conn = mysql.connect()
    # Once the connection is created, it is require a cursor to query our stored procedure. So, using conn connection, create a cursor.
    cursor = conn.cursor()
    # Do not store passwards, store hashes of passwords
    _hashed_password = generate_password_hash(_password)

    # Call the procedure see Muzapi notes' document (or README). This inserts data to Muzapi.tbl_user
    cursor.callproc("sp_createUser", (_name, _email, _hashed_password))

    # If the procedure is executed successfully, then we'll commit the changes and return the success message.
    data = cursor.fetchall()

    if len(data) is 0:
        conn.commit()
        return json.dumps({"message": "User created successfully !"})
    else:
        return json.dumps({"error": str(data[0])})


@app.route("/showSignIn")
def showSignIn():
    """
    """
    return render_template("signin.html")


@app.route("/validateLogin", methods=["POST"])
def validateLogin():
    """
    When a user submits a form, this method is called to validate whether the entered pass and login match the stored
    credentials.

    ** NOTE **: Note how we are passing an error to our error.html doc
    """
    try:
        _username = request.form["inputEmail"]
        _password = request.form["inputPassword"]

        # Create MySQL connection to retrieve all the stored user credentials with the stored procedure
        # TODO: still dont rly understand what is a cursor
        cursor = mysql.connect().cursor()
        # Call the procedure and get all the data in
        cursor.callproc("sp_validateLogin", (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                # If an user has been validated he receives an identity (his/her name = data[0][0]) in the session so he/she can access the homeUser page and others not.
                session["user"] = data[0][0]
                return redirect("/userHome")
            else:
                return render_template(
                    "error.html", error="Wrong Email address or Password."
                )
        else:
            return render_template(
                "error.html", error="Wrong Email address or Password."
            )

    except Exception as e:
        return render_template("error.html", error=str(e))


@app.route("/userHome")
def userHome():
    """
    Create method which would return the home user page.
    """
    if session.get("user"):
        return render_template("userHome.html")
    else:
        return render_template("error.html", error="Unauthorized Access")


@app.route("/logout")
def logOut():
    """
    Erase the name of the user from the flask.session so homepage is no longer accessible.
    """
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run()
