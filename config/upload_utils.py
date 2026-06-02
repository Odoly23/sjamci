import os
from uuid import uuid4

def upload_estado(instance, filename):
	upload_to = 'benifisiariu_files/{}'.format(instance.id)
	field = 'estado'
	ext = filename.split('.')[-1]
	if instance.pk:
		filename = '{}_{}.{}'.format(field,instance.id,ext)
	else:
		filename = '{}.{}'.format(uuid4().hex, ext)
	return os.path.join(upload_to, filename)


def upload_photo(instance, filename):
	upload_to = 'benefisiariu_files/{}'.format(instance.benefisiariu.id)
	field = 'photo'
	ext = filename.split('.')[-1]
	if instance.pk:
		filename = '{}_{}.{}'.format(field,instance.benefisiariu.id,ext)
	else:
		filename = '{}.{}'.format(uuid4().hex, ext)
	return os.path.join(upload_to, filename)

def upload_financial_book(instance, filename):
    business_id = instance.monitoring.business.id
    upload_to = f'financial_books/{business_id}'
    field = 'financial_book'
    ext = filename.split('.')[-1]
    if instance.pk:
        filename = f'{field}_{instance.id}.{ext}'
    else:
        filename = f'{uuid4().hex}.{ext}'
    return os.path.join(upload_to, filename)