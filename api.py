from flask import Flask, make_response, jsonify, request, current_app
from flask_mysqldb import MySQL
from functools import wraps
import xmltodict

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "db_myhotel"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["SITE_USER"] = "larry"
app.config["SITE_PASS"] = "12345"

mysql = MySQL(app)


def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

#authentication
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if (
            auth
            and auth.username == current_app.config["SITE_USER"]
            and auth.password == current_app.config["SITE_PASS"]
        ):
            return f(*args, **kwargs)
        return make_response(
            "<h1>Access denied!</h1>",
            401,
            {"WWW-Authenticate": 'Basic realm="Login required!"'},
        )

    return decorated


@app.route("/")
@auth_required
def hello_world():
    return "<p>Welcome to My Final Drill. My name is Larry John</p>"


# guest
@app.route("/guests", methods=["GET"])
@auth_required
def get_guest():
    frmt = request.args.get("format")
    if frmt == "xml":
        data = data_fetch("""select * from guest """)
        xml_data = xmltodict.unparse({"guest": {"guest": data}})
        response = make_response(xml_data)
        response.headers["Content-Type"] = "application/xml"
        return response

    else:
        data = data_fetch("""select * from guest""")
        return make_response(jsonify(data), 200)


@app.route("/guests/<int:id>", methods=["GET"])
@auth_required
def get_guest_byID(id):
    data = data_fetch("""select * from guest Where Guest_Id = {}""".format(id))
    return make_response(jsonify(data), 200)


@app.route("/guests/search", methods=["GET"])
@auth_required
def search_guests():
    first_name = request.args.get("firstname")
    last_name = request.args.get("lastname")

    if not first_name and not last_name:
        return make_response(jsonify({"error": "Please provide at least first name or last name"}), 400)

    conditions = []

    if first_name:
        conditions.append(f"FirstName LIKE '%{first_name}%'")

    if last_name:
        conditions.append(f"LastName LIKE '%{last_name}%'")

   
    data = data_fetch("SELECT * FROM guest WHERE " + " and ".join(conditions))
    if not data:
        return make_response(jsonify({"message": "No data found"}), 200)
    return make_response(jsonify(data), 200)


@app.route("/guests/<int:id>/booking", methods=["GET"])
@auth_required
def get_booking_ByGuest(id):
    data = data_fetch(
        """
        select Booking_Id,booking.Guest_Id,Check_In_Date,Check_Out_Date, FirstName,LastNAme,PhoneNumber
        from guest inner join booking on guest.Guest_Id=booking.Guest_Id 
        where guest.Guest_Id={}""".format(
            id
        )
    )
    return make_response(
        jsonify({"Guest_Id": id, "count": len(data), "booking": data}), 200
    )


@app.route("/guests", methods=["POST"])
@auth_required
def add_guest():
    cur = mysql.connection.cursor()
    info = request.get_json()
    FirstName = info["FirstName"]
    LastName = info["LastName"]
    PhoneNumber = info["PhoneNumber"]
    Email = info["Email"]

    cur.execute(
        """ INSERT INTO guest (FirstName, LastName,PhoneNumber, Email) VALUE (%s, %s, %s, %s)""",
        (FirstName, LastName, PhoneNumber, Email),
    )
    mysql.connection.commit()
    print("row(s) affected :{}".format(cur.rowcount))
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "guest added successfully", "rows_affected": rows_affected}
        ),
        201,
    )


@app.route("/guests/<int:id>", methods=["PUT"])
@auth_required
def update_guest(id):
    cur = mysql.connection.cursor()
    info = request.get_json()
    FirstName = info["FirstName"]
    LastName = info["LastName"]
    PhoneNumber = info["PhoneNumber"]

    cur.execute(
        """ UPDATE guest SET FirstName = %s, LastName = %s, PhoneNumber = %s WHERE Guest_Id = %s """,
        (FirstName, LastName, PhoneNumber, id),
    )
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "Guest updated successfully", "rows_affected": rows_affected}
        ),
        200,
    )


@app.route("/guests/<int:id>", methods=["DELETE"])
@auth_required
def delete_guest(id):
    cur = mysql.connection.cursor()
    cur.execute(""" DELETE FROM guest where Guest_Id = %s """, (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "Guest deleted successfully", "rows_affected": rows_affected}
        ),
        200,
    )

# booking and roomtype
@app.route("/bookings", methods=["GET"])
@auth_required
def get_gbooking():
    data = data_fetch("""select * from booking """)
    return make_response(jsonify(data), 200)


@app.route("/Room_types", methods=["GET"])
@auth_required
def get_roomtype():
    data = data_fetch("""select * from room_type """)
    return make_response(jsonify(data), 200)


if __name__ == "__main__":
    app.run(debug=True)
