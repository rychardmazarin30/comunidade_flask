from flask import Flask, render_template, url_for, request, flash, redirect, abort
from community.forms import FormCriarConta, FormEditPassword, FormLogin, FormEditProfile, FormEditPassword, FormExcludeAccount, FormCreatePost, ExcludePost
from community.models import Usuario, Post
from flask_login import login_user, login_required, current_user, logout_user
from community import app, db
import bcrypt, secrets, os
from PIL import Image

@app.route('/', methods=['GET'])
def home():
    posts = Post.query.order_by(Post.id.desc())
    users = Usuario.query.all()

    return render_template('home.html', posts=posts, users=users)


@app.route("/membros")
@login_required
def membros():
    users = Usuario.query.all()
    return render_template("members.html", users=users)


@app.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    
    if form_login.validate_on_submit() and 'submit_button_login' in request.form:
        global usuario
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        login_user(usuario)
        flash("Login Efetuado com Sucesso!", 'alert-success')
        next_parameter = request.args.get('next')
        if next_parameter:
            return redirect(next_parameter)
        else:
            return redirect(url_for('home'))

    return render_template("login.html", form_login=form_login)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form_createAccount = FormCriarConta()

    if form_createAccount.validate_on_submit() and 'submit_button_registerAccount' in request.form:
        
        # Criptografando senha usuário
        pw = form_createAccount.password.data
        pw = bytes(pw, 'utf-8')
        salt = bcrypt.gensalt(8)
        
        senha_cript = bcrypt.hashpw(pw, salt)
        # Cadastrando o usuário no banco de dados 
        usuario = Usuario(nome=form_createAccount.nome.data.capitalize(), sobrenome=form_createAccount.sobrenome.data.capitalize(), username=form_createAccount.username.data, email=form_createAccount.email.data, senha=senha_cript)
        db.session.add(usuario)
        db.session.commit()
        
        login_user(usuario)
        flash("Cadastro Efetuado com Sucesso!", 'alert-success')
        return redirect(url_for('home'))
        
    return render_template("cadastro.html", form_createAccount=form_createAccount)


@app.route("/profile")
@login_required
def profile():
    profile_photo = url_for('static', filename='profile_photos/{}'.format(current_user.foto_perfil))
    return render_template("profile.html", profile_photo=profile_photo)

def salvar_imagem(img):
    # Adicionar código a nome do arquivo para não haver conflito no db com equalNames
    codigo = secrets.token_hex(8)
    # seprando nome do arquivo da extensão
    nome, extensao = os.path.splitext(img.filename)
    # Juntando tudo: nome, codigo e extensão
    arquivo = nome + codigo + extensao
    # definindo caminho completo de onde sera salvo o arquivo da imagem
    complete_way = os.path.join(app.root_path, 'static/profile_photos', arquivo)
    
    # tupla para definir tamanho de largura e altura da imagem
    size = (400, 400)
    # reduzir imagem
    imagem_reduzida = Image.open(img)
    imagem_reduzida.thumbnail(size)
    # Salvar no banco de dados
    imagem_reduzida.save(complete_way)
    return arquivo
    
@app.route('/profile/edit', methods=["GET", "POST"])
@login_required
def edit_profile():
    form_edit = FormEditProfile()
    
    if request.method == 'GET':
        form_edit.nome.data = current_user.nome
        form_edit.sobrenome.data = current_user.sobrenome
        form_edit.username.data = current_user.username
        form_edit.email.data = current_user.email
    elif form_edit.validate_on_submit() and 'submit_button_edit' in request.form:
        user = current_user
        user.nome = form_edit.nome.data.capitalize()
        user.sobrenome = form_edit.sobrenome.data.capitalize()
        user.username = form_edit.username.data
        user.email = form_edit.email.data
        if form_edit.foto_perfil.data:
            nome_imagem = salvar_imagem(form_edit.foto_perfil.data)
            user.foto_perfil = nome_imagem

        if form_edit.tech_principal.data:
            user.tech_principal = form_edit.tech_principal.data
        
        db.session.commit()
        
        flash("Edição de Perfil Atualizada com Sucesso!", 'alert-success')
        return redirect(url_for('profile'))

    profile_photo = url_for('static', filename='profile_photos/{}'.format(current_user.foto_perfil))
    return render_template('profile_edit.html', profile_photo=profile_photo, form_edit=form_edit)


@app.route('/profile/edit/password', methods=["GET", "POST"])
@login_required
def edit_password():
    form_edit_password = FormEditPassword()
    
    if form_edit_password.validate_on_submit() and 'submit_button_edit_password' in request.form:
        pw = form_edit_password.new_password.data
        pw = bytes(pw, 'utf-8')
        salt = bcrypt.gensalt(8)

        senha_cript = bcrypt.hashpw(pw, salt)
        user = current_user
        user.senha = senha_cript
        db.session.commit()
        
        flash("Senha Atualizada com Sucesso!", 'alert-success')
        return redirect(url_for('profile'))
    
    return render_template('profile_edit_password.html', form_edit_password=form_edit_password)


@app.route('/profile/edit/exclude_account', methods=["GET", "POST"])
@login_required
def exclude_account():
    form_exclude = FormExcludeAccount()
    
    if form_exclude.validate_on_submit() and 'submit_button_exclude' in request.form:
        posts = Post.query.all()
        for post in posts:
            if current_user == post.autor:
                db.session.delete(post)
                db.session.commit()
            else:
                pass
        user = current_user
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash("Conta Excluida com sucesso!", 'alert-success')
        return redirect(url_for('home'))
    
    return render_template('exclude_account.html', form_exclude=form_exclude)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout Efetuado com Sucesso.', 'alert-success')
    return redirect(url_for('home'))


@app.route('/post/create', methods=["GET", "POST"])
@login_required
def create_post():
    form_create_post = FormCreatePost()
    if form_create_post.validate_on_submit():
        # Criando o Post e o inserindo no banco de dados
        post = Post(titulo=form_create_post.title.data, corpo=form_create_post.body.data, id_usuario=current_user.id)
        db.session.add(post)
        db.session.commit()
        # Redirecionando para a homepage e avisando o usuário que deu certo.
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form_create_post=form_create_post)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    
    return render_template('post.html', post=post)

@app.route('/post/editar/<post_id>/', methods=['GET', 'POST'])
@login_required
def editar_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCreatePost()
        if request.method == "GET":
            form.title.data = post.titulo
            form.body.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.title.data
            post.corpo = form.body.data
            db.session.commit()
            # Redirecionando para a homepage e avisando o usuário que deu certo.
            flash('Post Editado com Sucesso', 'alert-success')
            return redirect(url_for('home'))
    else:
        form = None

    return render_template('edit_post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        db.session.delete(post)
        db.session.commit()
        flash("Post Excluido com sucesso", "alert-danger")
        return redirect(url_for('home'))
    else:
        abort(403)