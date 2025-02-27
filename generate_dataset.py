import re
from read_raw_data import ReadRawData

class ReadData(ReadRawData):
    def __init__(self):
        super().__init__()
    
    def read_fem_file(self, file):
        for line in file:
            if re.match(r"^SPCADD", line):
                self.read_spc_subcase(line, mode='spc')
    
    def read_constr_file(self, file):
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
                print(sub_id)
            elif re.match(r'^\s+(\d+)', line):
                self.read_disp(line, sub_id)



def main():

    geom = open("/home/sces55/Malaika/fyp/data_processing/Var_1/FYP_HAT_QL_Model_MN_01a.nas", 'r')
    fem = open("/home/sces55/Malaika/fyp/data_processing/Var_1/Var_1.fem", 'r')
    constr = open("/home/sces55/Malaika/fyp/data_processing/Var_1/CBUSH_FORCE_SPC_V01.nas", 'r')
    pch = open("/home/sces55/Malaika/fyp/data_processing/Var_1/Var_1.pch", 'r')

    reader = ReadData()
    reader.read_geom_file(geom)
    reader.read_fem_file(fem)
    reader.read_constr_file(constr)
    reader.read_pch_file(pch)
    reader.organize_node_features()
    reader.create_edges()
    # from collections import Counter
    # Count nodes by type
    # type_counts = Counter(node['type'] for node in reader.node.values() if 'type' in node.keys())

    # Count nodes by thickness (ignoring None values)
    # thickness_counts = Counter(node['thickness'] for node in reader.node.values() if 'thickness' in node.keys() and node['thickness'] != None)

    # print("Nodes by Type:", type_counts)
    # print("Nodes by Thickness:", thickness_counts)
    # print("Nodes without type: ", no_types)

    return 0

if __name__ == "__main__":
    main()