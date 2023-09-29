from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import login_user, logout_user, current_user, login_required
from community.models import Usuario
import bcrypt

class FormCriarConta(FlaskForm):
    
    nome = StringField("Nome", validators=[DataRequired()])
    sobrenome = StringField("Sobrenome", validators=[DataRequired()])
    username = StringField("Nome de Usuário", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email("E-mail Inválido.")])
    password = PasswordField("Senha", validators=[DataRequired(), Length(8, 20, message="A sua senha tem que ter no mínimo 8 caracteres")])
    confirm_password = PasswordField("Confirmar Senha", validators=[DataRequired(), EqualTo('password', message="O campo deve ser igual a senha.")])
    submit_button_registerAccount = SubmitField("Cadastrar-se")
    
    # Necessário função chamar validate_ pois só assim o FlaskForm(), consegue entender ela como um validator.
    # Essa função faz com que cada usuario seja único, não deixando ter e-mails e nem usernames repetidos.
    def validate_email(self, email):
        usuario_email = Usuario.query.filter_by(email=email.data).first()
        if usuario_email:
            raise ValidationError('E-mail já cadastrado.')
        else:
            pass
        
    def validate_username(self, username):
        usuario_username = Usuario.query.filter_by(username=username.data).first()
        if usuario_username:
            raise ValidationError('Nome de Usuário já cadastrado.')
        else:
            pass
        

# Formulário de fazer login em sua conta.
class FormLogin(FlaskForm):
    
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(8, 20)])
    submit_button_login = SubmitField("Login")

    def validate_email(self, email):
        global user
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            pass
        else:
            raise ValidationError("E-mail Não encontrado.")
    
    def validate_senha(self, senha):
        senha = senha.data
        senha = bytes(senha, 'utf-8')
        
        if user:
            if bcrypt.checkpw(senha, user.senha):
                pass
            else:
                raise ValidationError("Senha Incorreta")
        else:
            pass


class FormEditProfile(FlaskForm):
    
    nome = StringField("Nome", validators=[DataRequired()])
    sobrenome = StringField("Sobrenome", validators=[DataRequired()])    
    username = StringField("Nome de Usuário", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email(message="E-mail Inválido.")])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    tech_principal = SelectField( choices=[('Não Informado', 'Tecnologia Principal'), ('Python', 'Python'), ('JavaScript', 'JavaScript'), ('PHP', 'PHP'), ('Ruby', 'Ruby'), ('C#', "C#"), ('C++', "C++"), ('Java', "Java"), ('Swift', "Swift"), ('Go', "Go")], validators=[DataRequired()])
    
    submit_button_edit = SubmitField("Editar Perfil")
    
    def validate_email(self, email):
        usuario_email = Usuario.query.filter_by(email=email.data).first()
        if usuario_email:
            if usuario_email.email == current_user.email:
                pass
            else:
                raise ValidationError('E-mail já cadastrado.')
        else:
            pass
        
    def validate_username(self, username):
        usuario_username = Usuario.query.filter_by(username=username.data).first()
        if usuario_username:
            if usuario_username.username == current_user.username:
                pass
            else:
                raise ValidationError('Nome de Usuário já cadastrado.')
        else:
            pass 
        
    
class FormEditPassword(FlaskForm):
    
    old_password = PasswordField("Senha", validators=[DataRequired(), Length(8, 20, message="A sua senha tem que ter no mínimo 8 caracteres")])
    new_password = PasswordField("Senha", validators=[DataRequired(), Length(8, 20, message="A sua senha tem que ter no mínimo 8 caracteres")])
    confirm_password = PasswordField("Confirmar Senha", validators=[DataRequired(), EqualTo('new_password', message="O campo deve ser igual a senha.")])
    submit_button_edit_password = SubmitField("Definir Senha")
    
    def validate_old_password(self, old_password):
        senha_velha = old_password.data
        senha_velha = bytes(senha_velha, 'utf-8')
        
        if bcrypt.checkpw(senha_velha, current_user.senha):
            pass
        else:
            raise ValidationError("Senha Antiga Incorreta")
    

class FormExcludeAccount(FlaskForm):
    
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(8, 20)])
    submit_button_exclude = SubmitField("Excluir Conta")
    
    def validate_email(self, email):
        
        if email.data == current_user.email:
            pass
        else:
            raise ValidationError("E-mail Incorreto.")
    
    def validate_senha(self, senha):
        senha = senha.data
        senha = bytes(senha, 'utf-8')
        
        if bcrypt.checkpw(senha, current_user.senha):
            pass
        else:
            raise ValidationError("Senha Incorreta.")
        
        
class FormCreatePost(FlaskForm):
    
    title = StringField("Titulo do Post", validators=[DataRequired(), Length(2, 140)])
    body = TextAreaField("Descrição", validators=[DataRequired(), Length(5, 280)])
    submit_button = SubmitField("Criar Post")
    
    
class ExcludePost(FlaskForm):
    
    submit_exclude = SubmitField("Confirmar")
    
    