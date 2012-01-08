editor = db(db.auth_group.role == 'editor')
if not editor.count():
    editor_id = db.auth_group.insert(role='editor')
else:
    editor_id = editor.select()[0].id

community = db(db.auth_group.role == 'community')
if not community.count():
    community_id = db.auth_group.insert(role='community')
else:
    community_id = community.select()[0].id

manager = db(db.auth_user.email == 'abhayashenoy@gmail.com')
if not manager.count():
    manager_id = db.auth_user.insert(
        manager=True,
        editor=True,
        registered=True,
        first_name='Abhaya',
        last_name='Shenoy',
        email='abhayashenoy@gmail.com',
        password='f583373c648485958e2315473d69ced7',
        rate='001',
        country='Singapore',
        dietary_preferences='None',
        tshirt='L',
        latitude=0.0,
        longitude=0.0,
        )
else:
    manager_id = manager.select()[0].id

if not db((db.auth_membership.group_id == editor_id) & (db.auth_membership.user_id == manager_id)).count():
    db.auth_membership.insert(group_id=editor_id, user_id=manager_id)
if not db((db.auth_membership.group_id == community_id) & (db.auth_membership.user_id == manager_id)).count():
    db.auth_membership.insert(group_id=community_id, user_id=manager_id)

db.commit()
