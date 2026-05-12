from user.models import Emp

def c_user_staff(user):
	objects = Emp.objects.filter(empuser__user=user).prefetch_related('empuser').first()
	obj = ""
	if obj: obj = objects
	return obj