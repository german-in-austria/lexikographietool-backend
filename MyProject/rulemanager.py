def can_add_lexeme_to_collection(collection,user):
    if user == None or collection == None:
        return False

    is_authorized = False
    ## if author
    is_authorized = is_authorized or user == collection.author

    
    ## if public allowed
    is_authorized = is_authorized or collection.public and collection.can_add_lexemes_public

    ## if group 
    if collection.group != None:
        #if group owner
        is_authorized = is_authorized or  user ==collection.group.owner

        #if group member and allowed
        is_authorized = is_authorized or user in collection.group.members.all() and collection.can_add_lexemes_group
    return is_authorized

def can_remove_lexeme_from_collection(collection,user):
    if user == None or collection == None:
        return False

    is_authorized = False
    ## if author
    is_authorized = is_authorized or user == collection.author

    
    ## if public allowed
    is_authorized = is_authorized or collection.public and collection.can_remove_lexemes_public

    ## if group 
    if collection.group != None:
        #if group owner
        is_authorized = is_authorized or  user ==collection.group.owner

        #if group member and allowed
        is_authorized = is_authorized or user in collection.group.members.all() and collection.can_remove_lexemes_group
    return is_authorized

def can_add_collection_to_group(group,user):
    if user == None or group == None:
        return False

    is_authorized = False

    #if group owner
    is_authorized = is_authorized or  user ==group.owner

    #if group member and allowed
    is_authorized = is_authorized or user in group.members.all() and group.settings.members_create_collection

    #if public and allowed
    is_authorized = is_authorized or group.settings.public and group.settings.public_create_collection
    return is_authorized


def can_see_lexemes_of_collection(collection,user):
    return collection.author == user or user.is_superuser or collection.public or (collection.group and (user in collection.group.members.all() or user == collection.group.owner))