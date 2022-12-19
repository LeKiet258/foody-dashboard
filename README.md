# foody-dashboard
Demo cho học phần Ứng dụng phân tích dữ liệu thông minh - 19_21


## Setup Python Environment
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install package virtualenv.

```bash
pip install virtualenv
```

After install virtualenv, cd to foody-dashboard folder and create environment name venv

```bash
python3 -m venv venv
```

Activate the Virtual Environment

```bash
source venv/bin/activate
```

Install requirement package

```bash
pip install -r requirement.txt
```

## Run
```bash
python3 manage.py makemigrations dashboard
python manage.py migrate dashboard
python3 manage.py runserver
```

## Note: 
Get all data from this [link](https://drive.google.com/drive/folders/1Mq4WZxsjxWxAfFDm83nCudfiAZHLvo07)

Recommend using python under 3.9 (tested with 3.8.10)

## Features
- Main page
- Show detail about one shop
- Compare 2 shop


## License

Free Software <3
