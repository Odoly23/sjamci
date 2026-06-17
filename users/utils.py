from django.contrib.auth.models import Group, User
from users.models import EmpUser


def tentukan_group(emp, position, division):
    if not position:
        return "staff"

    position_name = (
        position.position.name.upper()
        if position.position else ""
    )

    dn_code = (
        division.dn.code.upper()
        if division and division.dn
        else ""
    )

    dept_code = (
        division.department.code.upper()
        if division and division.department
        else ""
    )

    # Director Geral
    if "DIRECTOR GERAL" in position_name:
        return "admin"

    # Xefe Departamento
    if "XEFE DEPARTAMENTO" in position_name:
        return "XFD"

    # Departamento
    if dept_code == "KNI":
        return "KNI"

    if dept_code == "KS":
        return "KS"

    # Diresaun
    if dn_code == "DNIM":
        return "dnim"

    if dn_code in ["DNPE", "DNDI"]:
        return "mpms"

    return "staff"


def criar_ou_atualiza_user(emp):

    position = emp.positions.filter(
        is_active=True
    ).first()

    division = emp.divisions.filter(
        is_active=True
    ).first()

    group_name = tentukan_group(
        emp,
        position,
        division
    )

    empuser = EmpUser.objects.filter(
        emp=emp
    ).first()

    if not empuser:

        names = (emp.name or "").strip().split()

        first_name = names[0] if names else ""
        last_name = " ".join(names[1:]) if len(names) > 1 else ""

        username_base = f"{first_name.lower()}mci{emp.id}"

        username = username_base
        counter = 1

        while User.objects.filter(
            username=username
        ).exists():
            username = f"{username_base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            password='MCI@#2026',
            first_name=first_name,
            last_name=last_name,
        )

        empuser = EmpUser.objects.create(
            user=user,
            emp=emp
        )

    else:
        user = empuser.user

    user.groups.clear()

    try:
        group = Group.objects.get(
            name=group_name
        )
        user.groups.add(group)
    except Group.DoesNotExist:
        pass

    return user, group_name