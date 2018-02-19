import re

class Helper():
    def non_alphanumeric(self, string):
        return ''.join(ch for ch in string if ch.isalnum())

    def trim_spaces(self, string):
        return re.sub('\s+',' ', string.strip())

    def is_notEmpty(self, s):
        return bool(s and s.strip())

    def is_existInList(self, mlist, mval):
        return mval in mlist

    def is_contains(self, str, keyword):
        if str.find(keyword) != -1:
            return True
        else:
            return False

    def is_containsUnicode(self, s):
        try:
            s.encode('ascii')
        except UnicodeEncodeError:
            return False
        else:
            return True

    def safe_str(self, obj):
        try:
            return str(obj)
        except UnicodeEncodeError:
            # obj is unicode
            return unicode(obj).encode('unicode_escape')
        
    def resolveDirectory(self, directory):
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except:
                pass
    
    def trim_cellValue(self, input):
        input = self.trim_spaces(input)

        return (input
                .replace('\t', '')
                .replace('\n', '')
                .replace('\r\n', '')
                .replace('\n\r', '')
                .replace('\r', '')).strip()

    def get_urlParams(self, url, index):
        u = (url.split("&"))
        v = (u[index].split("="))
        return self.trim_cellValue(v[1])

    def trimAddress(self, address):
        return (address
                .replace(',  ,  , ', ', ')
                .replace(',  , ', ', ')
                .replace(',,', ', ')
                .replace(', ,', ', ')
                .replace(', , ,', ', ')
                .replace('null', '')).strip()

    def trimNull(self, string):
        strlist = []
        trm_str = string.split(" ")
        for index in range(0, len(trm_str)):
            value = trm_str[index]
            value = value.replace('null', '').replace('NULL', '').strip()
            if (self.is_notEmpty(value)):
                strlist.append(value)
        return ' '.join(strlist)

    def getTrimSubsName(self, subsname):
        subs =[]
        split_sub = subsname.split(" ")
        for index in range(0, len(split_sub)):
            value = split_sub[index]
            value = value.replace('null', '').replace('NULL', '').strip()
            if (self.is_notEmpty(value)):
                subs.append(value)

        return ' '.join(subs)


    def getTrimAddress(self, address):
        address_list = []
        splt_address = address.split(",")
        for index in range(0, len(splt_address)):
            value = splt_address[index]
            # value = value.replace('null','').replace('NULL','')
            value = self.trimNull(value)
            value = re.sub(r'[^a-zA-Z0-9=.#-+ ]', '', value).strip()

            if (self.is_notEmpty(value)):
                r_val = value = value.replace('.', '')
                if (self.is_notEmpty(r_val)):
                    address_list.append(value)

        return ', '.join(address_list)

    def getTrimContact(self, contact):
        contact_list = []
        prior_contact = []
        splt_contact = contact.split(",")
        for index in range(0, len(splt_contact)):
            value = splt_contact[index]
            value = value.strip()
            if (value.isdigit()):
                if ((len(value) == 10 and value.startswith('9')) or (len(value) == 11 and value.startswith('09'))):
                    prior_contact.append(value)
                else:
                    if ((len(value) == 9) or (len(value) == 7)):
                        contact_list.append(value)
        if (len(prior_contact) > 0):
            contacts = ', '.join(prior_contact)
        else:
            contacts = ', '.join(contact_list)
        return contacts
