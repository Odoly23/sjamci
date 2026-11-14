import hashlib
from django.contrib.auth.models import Group, User
from users.models import EmpUser
from django.db import transaction
from users.passwords import temporary_password
from seguransa.utils import require_password_change

def tentukan_group(emp, position, division):
    if not position or not position.position:
        return "staff"
    position_name = position.position.name.upper()
    if "DIRECTOR GERAL" in position_name: 
        return "admin"
    if "XEFE DEPARTAMENTO" in position_name: 
        return "XFD"
    if division:
        dept_code = division.department.code.upper() if division.department and division.department.code else ""
        dn_code = division.dn.code.upper() if division.dn and division.dn.code else ""
        gabinete_code = division.gabinete.code.upper() if division.gabinete and division.gabinete.code else ""
        if dept_code == "KNI":  
            return "KNI"
        if dept_code == "KS":  
            return "KS"
        if dn_code == "DNIM":  
            return "dnim"
        if dn_code == "DNPE": 
            return "mpms"
        if dn_code == "DNDI": 
            return "DNDI" 
        if gabinete_code == "GDGI":
            return "staff"
    return "staff"


def criar_ou_atualiza_user(emp):
    position = emp.positions.filter(is_active=True).first()
    division = emp.divisions.filter(is_active=True).first()
    group_name = tentukan_group(emp, position, division)
    with transaction.atomic():
        empuser = EmpUser.objects.filter(emp=emp).select_for_update().first()
        if not empuser:
            names = (emp.name or "").strip().split()
            first_name = names[0] if names else ""
            last_name = " ".join(names[1:]) if len(names) > 1 else ""
            if emp.email and User.objects.filter(email=emp.email).exists():
                user = User.objects.get(email=emp.email)
            else:
                username_base = f"{first_name.lower()}mci{emp.id}"
                username = username_base
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}{counter}"
                    counter += 1
                temp_password = temporary_password()
                user = User.objects.create_user(username=username, password=temp_password, email=emp.email, first_name=first_name, last_name=last_name)
                # Hatudu dala ida de'it ba administradór (la rai iha baze-dadus)
                user.temp_password = temp_password
                require_password_change(user)
            empuser, created = EmpUser.objects.get_or_create(emp=emp, defaults={'user': user})
            if not created:
                user = empuser.user
        else:
            user = empuser.user
        user.groups.clear()
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                try:
                    default_group = Group.objects.get(name="staff")
                    user.groups.add(default_group)
                except Group.DoesNotExist:
                    pass
                
    return user, group_name