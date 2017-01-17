'''
To import need to enter variation data into four tables:  1) new item ; 2) new PropertyValues; 3) new CatalogImages; 4) new SEOUrlKeywords;

'''
import pyodbc, uuid, csv, datetime
cnx = pyodbc.connect("Driver={SQL Server Native Client 11.0};Server=DELLPLEX2;Database=VirtoCommerce2;UID=virto;PWD=virto;")
today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
#make daetime compatible with sqlserver
today = today[:-3]
def get_uid():
    return uuid.uuid1()
def get_object_id(object_name, object_type):
    cursor = cnx.cursor()
    query = ("SELECT id FROM " + object_type + " WHERE Name = '" + str(object_name) + "'")
    cursor.execute(query)
    object_id = cursor.fetchone()
    cnx.commit()
    cursor.close()
    return object_id[0]

def get_property_id(property_type, property_name, property_value):
    cursor = cnx.cursor()
    query = ("SELECT id FROM Property where Name = '" + str(property_name) + "' and TargetType = '" + property_type + "'")
    cursor.execute(query)
    property_id = cursor.fetchone()
    query = ("SELECT id FROM PropertyDictionaryValue where Value = '" + str(property_value) + "' and PropertyId = '" + property_id[0] + "'")
    cursor.execute(query)
    property_id = cursor.fetchone()
    cnx.commit()
    cursor.close()
    return property_id[0]
def enter_property(my_value_guid, my_item, my_type, my_value, my_property_guid):
    cursor = cnx.cursor()
    query = ("Insert into PropertyValue(Id, Alias, Name, ValueType, KeyValue, ShortTextValue, DecimalValue, IntegerValue, BooleanValue, Locale, "
        "CreatedDate, ModifiedDate, CreatedBy, ModifiedBy, ItemId) "
        "values('" + my_value_guid + "','" + my_value + "','" + my_type + "',0,'" + my_property_guid  +  "','" + my_value + "','0.00',0,0,'en-US'"
        ",'" + str(today) + "','" + str(today) + "'," + "'admin','admin'" + ",'" + my_item + "')")
    cursor.execute(query)
    cnx.commit()
    cursor.close()
def enter_image(my_value_guid, my_item, my_image_name, my_order):
    cursor = cnx.cursor()
    query = ("Insert into CatalogImage(Id, [URL], [Name], [Group], SortOrder, ItemId, CreatedDate, ModifiedDate, CreatedBy, ModifiedBy) "
        "values('" + my_value_guid + "','" + "/catalog/" + my_image_name  + "','" + my_image_name + "','Images'," + str(my_order) + ",'" + my_item +
        "','" + str(today) + "','" + str(today) + "'," + "'admin','admin')")
    cursor.execute(query)
    cnx.commit()
    cursor.close()
reader = csv.DictReader(open('import.csv'))
for row in reader:
    category_guid = get_object_id(row['Category'],'Category')
    catalog_guid = get_object_id(row['Catalog'],'Catalog')
    brand_guid = get_property_id("Product", "brand", row['brand'])
    color_guid = get_property_id("Variation", "color", row['color'])
    size_guid = get_property_id("Variation", "size", row['size'])
    #remove hyphen from guid to match db guids format
    item_guid = str(get_uid()).replace('-','')
    #Enter the Item
    cursor = cnx.cursor()
    query = ("Insert into Item(Id, Name, StartDate, IsActive, IsBuyable, AvailabilityRule, MinQuantity, MaxQuantity, TrackInventory, Code, "
             "CatalogId, CreatedDate, ModifiedDate, CreatedBy, ModifiedBy, ParentId, ProductType, CategoryId, Priority) "
             "values('" + item_guid + "','" + str(row['Name']) + "','" + str(today) + "',1,1,0,'1.00','0.00',1,'" + str(row['Sku']) + "','" + str(catalog_guid)
             + "','" + str(today) + "','" + str(today) + "'," + "'admin','admin'" + ",'" + str(row['MainProductId']) + "','Physical','" + str(category_guid)
             + "',0)")
    cursor.execute(query)
    cnx.commit()
    cursor.close()
    #Now enter the brand Property
    property_guid = str(get_uid()).replace('-','')
    enter_property(property_guid, str(item_guid), 'brand', str(row['brand']), str(brand_guid))
    #Now enter the color Property
    property_guid = str(get_uid()).replace('-','')
    enter_property(property_guid, str(item_guid), 'color', str(row['color']), str(color_guid))
    #Now enter the size Property
    property_guid = str(get_uid()).replace('-','')
    enter_property(property_guid, str(item_guid), 'size', str(row['size']), str(size_guid))
    #Now enter primary image
    image_guid = str(get_uid()).replace('-','')
    enter_image(image_guid,str(item_guid),str(row['PrimaryImage']), 0)
    #enter Images 2-4 if available
    if str(row['SecondImage']) != '':
        image_guid = str(get_uid()).replace('-', '')
        enter_image(image_guid, str(item_guid), str(row['SecondImage']), 1)
    if str(row['ThirdImage']) != '':
        image_guid = str(get_uid()).replace('-', '')
        enter_image(image_guid, str(item_guid), str(row['ThirdImage']), 2)
    if str(row['ForthImage']) != '':
        image_guid = str(get_uid()).replace('-', '')
        enter_image(image_guid, str(item_guid), str(row['ForthImage']), 3)
    #Now enter the SEOKeywords for the item
    seo_guid = str(get_uid()).replace('-','')
    strTitle = str(row['brand']) + ' ' +  str(row['Name']) + " color " + str(row['color']) + " size " + str(row['size'])
    strDesc = "Koda by Chameleon E-Store presents " + strTitle
    strImgAlt = str(row['brand'])+ ' ' + str(row['Name'])
    cursor = cnx.cursor()
    query = ("Insert into SeoUrlKeyword(Id, [Language], Keyword, IsActive, CreatedDate, ModifiedDate, CreatedBy, ModifiedBy, ObjectId, ObjectType, "
    "Title, MetaDescription, ImageAltDescription, StoreId) "
    "values('" + seo_guid + "','en-US','" + str(row['Name']).replace(' ', '-').lower() + "',0,'" + str(today) + "','" + str(today) + "'," + "'admin','admin','"
    + image_guid + "','CatalogProduct','" + strTitle + "','" + strDesc + "','" + strImgAlt + "','koda')")
    cursor.execute(query)
    cnx.commit()
    cursor.close()



