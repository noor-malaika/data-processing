import re
from read_raw_data import ReadRawData

class ReadData(ReadRawData):

    def __init__(self):
        super().__init__()
        self.constr = "/home/sces55/Malaika/fyp/data_processing/Var_1/CBUSH_FORCE_SPC_V01.nas"
        self.fem = "/home/sces55/Malaika/fyp/data_processing/Var_1/Var_1.fem"

    def _read_fem_file(self, file_path=None):
        if file_path is None:
            file_path = self.fem
        with open(file_path, 'r') as file:
            for line in file:
                if re.match(r"^SPCADD", line):
                    self.read_spc_subcase(line, mode='spc')

    def read_constr_file(self, file_path=None):
        if file_path is None:
            file_path = self.constr

        self._read_fem_file()
        with open(file_path, 'r') as file:
            for line in file:
                if re.match(r'^SPC', line):
                    self.read_spc(line, mode='spc')
            ## force was manually set
    
    def read_geom_file(self, file):
        rbe_f = "" # flag for reading rbe cont lines
        rb2_id, rb3_id = None,None
        for line in file:
            if re.match(r'^GRID', line):
                self.read_gen(line, mode='node')
            elif re.match(r'^CTRIA3', line):
                self.read_gen(line, mode='tria')
            elif re.match(r'^PSHELL', line):
                self.read_gen(line, mode='pshell')
            elif re.match(r'^RBE2', line):
                rb2_id = self.read_rbe(line, mode='rb2')
                rbe_f = 'rb2'
            elif re.match(r'^\+', line) and rbe_f == 'rb2' and rb2_id:
                self.read_rbe(line, mode='rb2', cont=True, rid=rb2_id)
            elif re.match(r'^RBE3', line):
                rb3_id = self.read_rbe(line, mode='rb3')
                rbe_f = 'rb3'
            elif re.match(r'^\+', line) and rbe_f == 'rb3' and rb3_id:
                self.read_rbe(line, mode='rb3', cont=True, rid=rb3_id)
            else:
                rb2_id, rb3_id, rbe_f = None, None, ""

    def read_pch_file(self, file):
        sub_id = None
        for line in file:
            if re.match(r'^\$SUBCASE', line):
                sub_id = re.search(r'(\d+)', line).group(1)
            elif re.match(r'^\s+(\d+)', line):
                self.read_disp(line, sub_id)
    
    def read(self, geom_file, pch_file):
        self.read_geom_file(geom_file)
        self.read_pch_file(pch_file)
        self.organize()



def main():
    reader = ReadData()
    reader.read_constr_file() # spc is file read once, force data has been manually set
    geom = open("/home/sces55/Malaika/fyp/data_processing/Var_1/FYP_HAT_QL_Model_MN_01a.nas", 'r')
    pch = open("/home/sces55/Malaika/fyp/data_processing/Var_1/Var_1.pch", 'r')

    
    reader.read(geom, pch)

    return 0

if __name__ == "__main__":
    main()