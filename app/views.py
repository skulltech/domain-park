from flask import render_template, request, url_for, flash, session, redirect, abort
from app import app, db, models
from .forms import LoginForm, AddFolderForm, AddDomainForm, SelectFolderForm, ParkingcrewCredsForm, AlpnamesCredsForm, RookmediaCredsForm, SelectAccountForm
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

    account_type = request.args.get('account')
    account_name = request.args.get('name')

    if not (account_type and account_name):
        form = SelectAccountForm()

        with open('credentials.json', mode='r') as f:
            creds = json.load(f)

        choices = []
        for key in creds['parkingcrew']:
            choices.append(('pc' + key, 'Parkingcrew : ' + key))
        for key, value in creds['alpnames'].items():
            choices.append(('an' + key, 'Alpnames : ' + key))
        for key, value in creds['rookmedia'].items():
            choices.append(('rm' + key, 'Rookmedia : ' + key))

        form.account_name.choices = choices

        if request.method == 'POST' and form.validate():
            account = form.account_name.data[:2]
            name = form.account_name.data[2:]
            return redirect(url_for('edit_credentials', account=account, name=name))

        return render_template('select-account.html', title='Select Account', form=form)

    with open('credentials.json', mode='r') as f:
        creds = json.load(f)

    if account_type == 'pc':
        form = ParkingcrewCredsForm(account_name=account_name, username=creds['parkingcrew'][account_name]['username'], api_key=creds['parkingcrew'][account_name]['api_key'])
        if request.method == 'POST' and form.validate():
            del creds['parkingcrew'][account_name]
            creds['parkingcrew'][form.account_name.data] = {'username': form.username.data, 'api_key':form.api_key.data}
            with open('credentials.json', mode='w') as f:
                json.dump(creds, f)
            flash('The account {} is successfully edited'.format(form.account_name.data), 'success')
            return redirect('/home')
        return render_template('parkingcrew-credentials.html', title='Edit Parkingcrew Account', form=form)

    elif account_type == 'rm':
        form = RookmediaCredsForm(account_name=account_name, guid=creds['rookmedia'][account_name]['guid'])
        if request.method == 'POST' and form.validate():
            del creds['rookmedia'][account_name]
            creds['rookmedia'][form.account_name.data] = {'guid': form.guid.data}
            with open('credentials.json', mode='w') as f:
                json.dump(creds, f)
            flash('The account {} is successfully edited'.format(form.account_name.data), 'success')
            return redirect('/home')
        return render_template('rookmedia-credentials.html', title='Edit Rookmedia Account', form=form)
    
    elif account_type == 'an':
        form = AlpnamesCredsForm(account_name=account_name, reseller_id=creds['alpnames'][account_name]['reseller_id'], api_key=creds['alpnames'][account_name]['api_key'], customer_id=creds['alpnames'][account_name]['customer_id'])
        if request.method == 'POST' and form.validate():
            del creds['alpnames'][account_name]
            creds['alpnames'][form.account_name.data] = {'reseller_id': form.reseller_id.data, 'api_key':form.api_key.data, 'customer_id':form.customer_id.data}
            with open('credentials.json', mode='w') as f:
                json.dump(creds, f)
            flash('The account {} is successfully edited'.format(form.account_name.data), 'success')
            return redirect('/home')
        return render_template('alpnames-credentials.html', title='Edit Alpnames Account', form=form)

    else:
        flash('Invalid account type', 'error')
        return redirect('/home')

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