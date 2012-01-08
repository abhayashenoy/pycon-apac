import codecs

db(db.paper.id > 0).delete()

lines = []
with codecs.open('talks.txt', encoding='utf-8') as f:
  for l in f:
      lines.append(l.strip().split('\t'))

level = dict(map(lambda x: (x[1].lower(), x[0]), settings.difficulty))
recording = dict(map(lambda x: (x[1].lower(), x[0]), settings.permissions))
creator = db(db.auth_user.email == 'abhayashenoy@gmail.com').select().first()

lines[0][0] = u'status'
lines[0] = [l.encode('ascii') for l in lines[0]]

for l in lines[1:]:
  l[5] = level[l[5].lower()]
  l[6] = recording[l[6].lower()]
  for i in range(1, 9):
    if i in (5, 6) or not l[i]:
      continue
    if l[i][0] == u'"':
      l[i] = l[i][1:]
    if l[i][-1] == u'"':
      l[i] = l[i][:-1]
  p_id = db.paper.insert(**dict(zip(lines[0], l)))
  db.commit()
  db(db.paper.id == p_id).update(created_by=creator)

db.commit()
