import subprocess
class ArpTable(object):
    """description of class"""
    def validate_ip(self,s):
        a = s.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    def get_ips(self, opts):
        self.ips = []
        output = subprocess.check_output(("arp", "-a"))
        #print (output)
        output = output.decode("ascii") #decode output to ascii, to remove \b as binary indicator
        lines = output.splitlines()
        for line in lines:
            #print (line)
            s_lines = line.split()
            for s_line in s_lines:
                if self.validate_ip(s_line):
                    #print (s_line)
                    if opts and opts.strip():
                        if s_line.startswith(opts):
                            self.ips.append(s_line)
                    else:
                        self.ips.append(s_line)
        return self.ips
# USAGE:
'''
self.arp = ArpTable()
ips = self.arp.get_ips('192')
for ip in ips:
	print (ip)
'''




