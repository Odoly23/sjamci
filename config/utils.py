import os, datetime, hashlib, numpy
from base64 import b64encode, b64decode
from django.conf import settings
from calendar import monthrange

def getnewid(table_name):
	result = table_name.objects.last()
	if result:
		newid = result.id + 1
		hashid = hashlib.md5(str(newid).encode())
	else:
		newid = 1
		hashid = hashlib.md5(str(newid).encode())
	return newid, hashid.hexdigest()

def hash_md5(strhash):
	hashed = hashlib.md5(strhash.encode())
	return hashed.hexdigest()

def split_string(string):
	string2 = string.split()
	return string2[0].lower()

def save_picture(form_picture):
	image_parts = form_picture.split(";base64,")
	return image_parts

def read_picture(picture_column):
	image = b64encode(picture_column).decode("utf-8")
	image = image.split("/jpegbase64")
	return image[1]

def base64toImage(imgstring, empid):
	imgdata = b64decode(imgstring)
	filename = 'photo2_'+str(empid)+'.jpg'
	if not os.path.exists('media/employee_files/'):
		os.makedirs('media/employee_files/')
	path = settings.MEDIA_ROOT+"/employee_files/"+empid+"/"+filename
	with open(path, 'wb') as f:
		f.write(imgdata)

def file_extention(fupload):
	_, f_ext = os.path.splitext(fupload.name)
	return f_ext

def f_monthname(month):
	m = ['Janeiru','Fevereiru','Marsu','Abril','Maiu','Junhu','Julhu','Agostu','Setembru',
		'Outubru','Novembru','Dezembru']
	return m[month-1]

def f_monthname_por(month):
	m = ['Janeiro','Fevereiro','Marco','Abril','Maio','Junho','Julho','Agosto','Setembro',
		'Outubro','Novembro','Desembro']
	return m[month-1]

def f_monthname_eng(month):
	m = ['January','February','March','April','May','June','July','August',\
		'September','October','November','Desember']
	return m[month-1]

def f_monthlist():
	m = numpy.linspace(start = 1, stop = 12, num = 12)
	months = []
	for j in m:
		months.append([int(j),f_monthname_eng(int(j))])
	return months

def number_of_days_in_month(year=2019, month=2):
    return monthrange(year, month)[1]

def f_card_expiry(start_date):
	date_1 = datetime.datetime.strptime(str(start_date), "%Y-%m-%d")
	date_2 = datetime.date(date_1.year + 4, date_1.month, date_1.day)
	return date_2.strftime("%Y-%m-%d")

def f_date_interval(start_date,end_date):
	date_1 = datetime.datetime.strptime(str(start_date), "%Y-%m-%d")
	date_2 = datetime.datetime.strptime(str(end_date), "%Y-%m-%d")
	return date_2 - date_1