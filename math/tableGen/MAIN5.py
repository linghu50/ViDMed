import xlrd
import json
import string

mood_path = 'excel/Low arouse & Low value.xlsx'
emotion = 'sad'
# #
# mood_path = 'excel/High arouse & Low value.xlsx'
# emotion = 'angry'
# #
# mood_path = 'excel/High arouse & High value.xlsx'
# emotion = 'happy'

# mood_path = 'excel/Low arouse & High value.xlsx'
# emotion = 'peace'


workBook = xlrd.open_workbook(mood_path)
cols = workBook.sheet_by_index(0).col_values(7)
id = []
for data in cols:
    if type(data) == type(1.0):
        id.append(data)
print(json.dumps(id))
