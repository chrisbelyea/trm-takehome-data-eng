# Exercise submission
- For solution overview and architecture see [SOLUTION](./SOLUTION.md).
- For deployment and validation instructions see [DEPLOY](./DEPLOY.md).

Thank you for your time! I know it's limited & valuable. :smile:


## Overview

This repo provides the boiler plate required to setup the API for the takehome BONUS section.

This repo assumes:
- Familiarity with Python
- Understanding of basic HTTP request semantics
- Installed Conda as a package manager

## Getting Started

**1. Create your Conda Environment**
`conda create -n <env_name> python=3.8`

**2. Install the required dependencies**
`conda install -n <env_name> requirements.txt`

**3. Run the local flask Development Server**
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

**4. Hit the endpoint from your local browser**
Enter `http://127.0.0.1:5000/address/exposure/direct?address=1BQAPyku1ZibWGAgd8QePpW1vAKHowqLez` into your browser!

You should see the following response:
```
{
  "data": [
    { "address": "1FGhgLbMzrUV5mgwX9nkEeqHbKbUK29nbQ", "inflows": "0", "outflows": "0.01733177", "total_flows": "0.01733177" },
    { "address": "1Huro4zmi1kD1Ln4krTgJiXMYrAkEd4YSh", "inflows": "0.01733177", "outflows": "0", "total_flows": "0.01733177" },
  ],
  "success": True
}
```

## Additional Details

Depending on your data store, you may have to install one or more packages
to connect via Python. I have listed the most common packages below:
- RedShift/Postgres: [Psycopg2](https://pypi.org/project/psycopg2/)
- MySQL: [mysqlclient](https://pypi.python.org/pypi/mysqlclient)
- BigQuery: [google-cloud-bigquery](https://pypi.org/project/google-cloud-bigquery/)
