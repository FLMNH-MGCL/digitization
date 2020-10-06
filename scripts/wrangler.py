import gspread # https://gspread.readthedocs.io/en/latest/index.html

gc = gspread.service_account(filename='config.json')

sh = gc.open_by_key('1IIAp5sDSq61x1ZRmtbtcOSXoJ0QglJtilI6M6gUY3Dw')

worksheets = sh.worksheets()

seq_id_worksheet = worksheets[0]

seq_id_headers = seq_id_worksheet.row_values(1)

print(seq_id_headers)


"""
wrangler overview:

CREATE DICTIONARY
==================
given excel sheet:
  make dictionary -> map MGCL nums to specimen info
  loop rows:
    location obj: { dorsal, ventral, parent_directory }
    specimen obj: { bombID, catalogNumber, otherCatalogNumber, family, genus, sepcies, recordId, refs, location_obj }
    { catalogNumber : specimen_obj }

CHECK IMG EXISTENCE IN FS
=========================
given provided start in filesystem:
  grab all files
  loop files:
    destructure path to obtain family, genus, species
    destructure filename to object mgcl
    attempt access of dictionary by mgcl
      if success -> update object with location data

OBTAIN UI
============
load premade dictionary of UIs
loop dictionary entries:
  attempt access of UI by family, genus, species
    if get UI -> assign object bombID

then what?
"""