from flask import render_template, request, url_for, flash, session, redirect, abort
from app import app, db, models
from .forms import LoginForm, AddFolderForm, AddDomainForm, SelectFolderForm, EditCredentialsForm
from .core import AlpNames, RookMedia, ParkingCrew
import json


@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def home_page():
    if not session.get('logged_in'):
        return redirect('/login')

    return render_template('index.html')

@app.route('/show-folders', methods=['POST', 'GET'])
def show_folders():
    if not session.get('logged_in'):
        return redirect('/login')

    entries = models.Folders.query.order_by(models.Folders.folder).all()
    return render_template('show-folders.html', folders=entries)

@app.route('/delete-folder', methods=['POST', 'GET'])
def delete_folder():
    if not session.get('logged_in'):
        return redirect('/login')

    form = SelectFolderForm()

    entries = models.Folders.query.all()
    form.folder_name.choices = [(e.id, e.folder) for e in entries]

    if request.method == 'POST' and form.validate():
        user = models.Folders.query.get(form.folder_name.data)
        db.session.delete(user)
        db.session.commit()
        flash('The selected folder is deleted', 'success')

        return redirect('/home')

    return render_template('select-folder.html', title='Delete Folder', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None

    with open('credentials.json') as f:
        credentials = json.load(f)

    if request.method == 'POST' and form.validate():
        if form.username.data != credentials['master']['username']:
            error = 'Invalid Username'
        elif form.password.data != credentials['master']['password']:
            error = 'Invalid Password'
        else:
            session['logged_in'] = True
            flash('You were logged in', 'success')
            return redirect('/home')

    return render_template('login.html', title='Sign In', form=form, error=error)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'success')
    return redirect('/home')


@app.route('/add-folder', methods=['POST', 'GET'])
def add_folder():
    if not session.get('logged_in'):
        return redirect('/login')

    form = AddFolderForm()
    error = None

    if request.method == 'POST' and form.validate():
        keywords = json.dumps(form.keywords.data.splitlines())

        k = models.Folders(folder=form.folder_name.data, keywords=keywords)
        db.session.add(k)
        db.session.commit()

        flash('The Folder is successfully added to the Database', 'success')
        return redirect('/home')

    return render_template('add-folder.html', title='Add Folder', form=form, error=error)

@app.route('/edit-folder', methods=['GET', 'POST'])
def edit_folder():
    if not session.get('logged_in'):
        return redirect('/login')

    folder_id = request.args.get('folderID')
    if not folder_id:
        form =SelectFolderForm()

        entries = models.Folders.query.all()
        form.folder_name.choices = [(e.id, e.folder) for e in entries]

        if request.method == 'POST' and form.validate():
            user = models.Folders.query.get(form.folder_name.data)
            return redirect(url_for('edit_folder', folderID=form.folder_name.data))

        return render_template('select-folder.html', title='Edit Folder', form=form)
        
    entry = models.Folders.query.get(folder_id)
    form = AddFolderForm(folder_name=entry.folder, keywords='\n'.join(json.loads(entry.keywords)))

    if request.method == 'POST' and form.validate():
        keywords = json.dumps(form.keywords.data.splitlines())

        entry.folder = form.folder_name.data
        entry.keywords = json.dumps(form.keywords.data.splitlines())
        db.session.commit()

        flash('The Folder is edited', 'success')
        return redirect('/home')

    return render_template('add-folder.html', title='Edit Folder', form=form)

@app.route('/edit-credentials', methods=['GET', 'POST'])
def edit_credentials():
    if not session.get('logged_in'):
        return redirect('/login')

    with open('credentials.json', mode='r') as f:
        credentials = json.load(f)

    form = EditCredentialsForm(username = credentials['master']['username'],
        password = credentials['master']['password'],
        alpnames_reseller_id = credentials['alpnames']['reseller_id'], 
        alpnames_api_key = credentials['alpnames']['api_key'], 
        alpnames_customer_id = credentials['alpnames']['customer_id'], 
        parkingcrew_username_1 = credentials['parkingcrew']['1']['username'], 
        parkingcrew_api_key_1 = credentials['parkingcrew']['1']['api_key'],
        parkingcrew_username_2 = credentials['parkingcrew']['2']['username'], 
        parkingcrew_api_key_2 = credentials['parkingcrew']['2']['api_key'])
    error = None

    if request.method == 'POST' and form.validate():
        credentials['alpnames']['reseller_id'] = form.alpnames_reseller_id.data
        credentials['alpnames']['api_key'] = form.alpnames_api_key.data
        credentials['alpnames']['customer_id'] = form.alpnames_customer_id.data
        credentials['parkingcrew']['1']['username'] = form.parkingcrew_username_1.data
        credentials['parkingcrew']['1']['api_key'] = form.parkingcrew_api_key_1.data
        credentials['parkingcrew']['2']['username'] = form.parkingcrew_username_2.data
        credentials['parkingcrew']['2']['api_key'] = form.parkingcrew_api_key_2.data
        credentials['master']['username'] = form.username.data
        credentials['master']['password'] = form.password.data

        with open('credentials.json', mode='w') as f:
            json.dump(credentials, f)

        flash('The credentials are successfully edited', 'success')
        return redirect('/home')

    return render_template('edit-credentials.html', title='Edit Credentials', form=form, error=error)

@app.route('/add-domain', methods=['GET', 'POST'])
def add_domain():
    if not session.get('logged_in'):
        return redirect('/login')

    alpnames = AlpNames()
    form = AddDomainForm()
    error = None

    form.folder_name.choices = [(e.id, e.folder)
                                for e in models.Folders.query.order_by(models.Folders.folder).all()]
    try:                            
        form.contact.choices = alpnames.get_contacts()
    except:
        form.contact.choices = [('None', 'No contact Available!')]
        error = 'Could not connect to AlpNames API'

    if request.method == 'POST' and form.validate():
        if form.parker_name.data == 'pk1' or form.parker_name.data == 'pk2':
            nameservers = ['ns1.parkingcrew.net', 'ns2.parkingcrew.net']
        elif form.parker_name.data == 'rm':
            nameservers = ['ns1.alpnames.com', 'ns2.alpnames.com',
                           'ns3.alpnames.com', 'ns4.alpnames.com']

        if form.purchase.data == True:
            r = alpnames.register_domain(domain_name=form.domain_name.data, 
                privacy=form.purchase_privacy.data, nameservers=nameservers, 
                contact_id=int(form.contact.data))
            if r[0] == False:
                error = r[1]
        else:
            order_id = alpnames.get_order_id(domain_name=form.domain_name.data)
            alpnames.edit_nameservers(order_id=order_id, nameservers=nameservers)

        if form.parker_name.data == 'rm':
            alpnames.add_dns_record(domain_name=form.domain_name.data, host='www', address='208.73.209.168')
            alpnames.add_dns_record(domain_name=form.domain_name.data, host='@', address='208.73.209.168')

        keywords = json.loads(models.Folders.query.get(form.folder_name.data).keywords)

        if form.parker_name.data == 'pk1' or form.parker_name.data == 'pk2':
            if form.parker_name.data == 'pk1':
                parkingcrew = ParkingCrew('1')
            else:
                parkingcrew = ParkingCrew('2')
            folder_name = models.Folders.query.get(form.folder_name.data).folder
            folder_id = parkingcrew.get_folder_id(folder_name=folder_name)

            if not folder_id:
                folder_id = parkingcrew.add_folder(folder_name=folder_name)[1]
            
            parkingcrew.add_domain(domain_name=form.domain_name.data, folder_id=folder_id)
            parkingcrew.add_keywords(domain_name=form.domain_name.data, keywords=keywords)

        flash('The Domain is successfully added', 'success')
        return redirect('/home')

    return render_template('add-domain.html', title='Add Domain', form=form, error=error)