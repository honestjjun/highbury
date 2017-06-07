from django.contrib.auth.base_user import BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, email, nickname, sex, date_of_birth, password=None):
        if not email:
            return ValueError('You have to input your e-mail')
        user = self.model(
            email = self.normalize_email(email),
            nickname = nickname,
            sex = sex,
            date_of_birth = date_of_birth
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, nickname, sex, date_of_birth, password):
        user = self.create_user(
            email = email,
            nickname = nickname,
            sex = sex,
            date_of_birth = date_of_birth,
            password = password
        )
        user.is_superuser = True
        user.save()

        return user
