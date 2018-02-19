import time

class AppointmentHelper(object):
    """description of class"""
    def get_value(self, description):
        values = []
        if description and description.strip():
            descs = description.split('-')
            if len(descs) >0:
                for d in range(0,len(descs)-1):
                    values.append(descs[d].strip())
                return '-'.join(values)
        return ''

    def get_Filter(self, cabinetNo):
        pass

    def get_currentDate(self):
        return time.strftime("%m/%d/%Y")





