from django import forms

from .models import MyUser


class MyUserForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput,)

    def __init__(self, *args, **kwargs):
        super(MyUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:360px; font-size:13px; height:36px; color:#4a4a4a;',
            'placeholder': 'E-mail'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:360px; font-size:13px; height:36px; color:#4a4a4a;',
            'placeholder': 'Password'
        })


class MyUserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput,)
    password2 = forms.CharField(widget=forms.PasswordInput,)

    class Meta:
        model = MyUser
        fields = ('email', 'password1', 'password2', 'nickname', 'sex', 'date_of_birth', 'photo', 'tel', 'address')

    def __init__(self, *args, **kwargs):
        super(MyUserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'style': 'float:left; width:610px; font-size:14px; height:36px; color:#4a4a4a;',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:610px; font-size:13px; color:#4a4a4a; height:36px;',
            'placeholder': '비밀번호를 입력해주세요'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:610px; font-size:13px; color:#4a4a4a; height:36px;',
            'placeholder': '비밀번호를 입력해주세요'
        })
        self.fields['nickname'].widget.attrs.update({
            'class': 'form-control',
            'id': 'highbury-nickname',
            'style': 'width:415px; font-size:13px; color:#4a4a4a; height:36px;',
            'placeholder': '닉네임을 입력해주세요'
        })
        self.fields['photo'].widget.attrs.update({
            'class': 'form-control',
            'style': 'font-size:13px; color:#4a4a4a; height:36px; width:330px;'
        })
        self.fields['tel'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:610px; font-size:13px; color:#4a4a4a; height:36px;',
            'placeholder': '전화번호를 입력해주세요'
        })
        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'style':'width:610px; font-size:13px; color:#4a4a4a; height:36px;',
        })


class MyUserProfileForm(forms.ModelForm):
    class Meta:
        model= MyUser
        fields = ('photo','tel', 'address')

    def __init__(self, *args, **kwargs):
        super(MyUserProfileForm, self).__init__(*args, **kwargs)
        self.fields['tel'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:680px; font-size:13px; color:#4a4a4a;'
        })
        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width:680px; font-size:13px; color:#4a4a4a;'
        })


class NicknameForm(forms.Form):
    nickname = forms.CharField(max_length=40)


class PasswordChangeForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, )
    password2 = forms.CharField(widget=forms.PasswordInput, )

    class Meta:
        model = MyUser
        fields = ('email', 'password1', 'password2', 'nickname')


class PasswordResetForm(forms.ModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('old_password', 'new_password1', 'new_password2')
