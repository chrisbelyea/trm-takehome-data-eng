import os

from flask import Flask, request
import psycopg2

# TODO: Error handling for when required values aren't set
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", "5432")


app = Flask(__name__)

def get_database_version()
    dbcon = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    cursor = dbcon.cursor()
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    print(data)  # TODO: Logger would be more appropriate
    dbcon.close()

@app.route("/address/exposure/direct", methods=["GET"])
def address_exposure_direct():
    address = request.args.get("address", "")
    start_date = request.args.get("start_date", "0001-01-01T00:00:00Z")
    end_date = request.args.get("end_date", "9999-12-31T23:59:59Z")
    flow_type = request.args.get("flow_type", "both")
    limit = request.args.get("limit", 100)
    offset = request.args.get("offset", 0)

    sample_res = {
        "data": [
            {
                "address": "1FGhgLbMzrUV5mgwX9nkEeqHbKbUK29nbQ",
                "inflows": "0",
                "outflows": "0.01733177",
                "total_flows": "0.01733177",
            },
            {
                "address": "1Huro4zmi1kD1Ln4krTgJiXMYrAkEd4YSh",
                "inflows": "0.01733177",
                "outflows": "0",
                "total_flows": "0.01733177",
            },
        ],
        "success": True,
    }

    # Pretend there's some meaningful query that's supposed to happen
    get_database_version()

    return sample_res



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
