###NOTE: This script uses a lot of indexing, couldn't be understood without references (CBUSH_FORCE_SPC.nas, FYP_model.nas)
"""spc and force components r same everywhere, don't need to read them for all variants"""
import copy
class ReadRawData:
    def __init__(self):
        self.inputs = {}
        self.node = {}
        self.tria = {}
        self.rb2 = {}
        self.rb3 = {}
        self.pshell = {}
        self.spc = {}
        self.force = {
            '805': {
                'nid': "74026",
                'force': [0, 4000, 0],
            },
            '806': {
                'nid': "74027",
                'force': [0, 4000, 0],
            }
        }
        self.outputs = {
            '805': {},
            '806': {},
        }
        self.material = {}

    def split_components(self,line):
        vals = [line[i:i+8].strip() for i in range(0, len(line), 8) if line[i:i+8].strip()]
        return vals

    def read_gen(self, line, mode):
        # trias, grids, pshell, material
        vals = self.split_components(line)
        try:
            getattr(self, mode)[vals[1]] = {'data':tuple(vals[2:])}
        except:
            raise Exception(f"Couldn't read {mode} data.")

    def read_rbe(self, line, mode, cont=False, rid=None):
        vals = self.split_components(line)
        try:
            if cont:
                getattr(self, mode)[rid]['data'] += tuple(vals[1:])
            else:
                rid = vals[1]
                getattr(self, mode)[rid] = {'data':tuple(vals[2:])}
                return rid
        except:
            raise Exception(f"Couldn't read {mode} data.")

    ### this function needs tobe changed
    def read_spc_subcase(self, line, mode):
        ## read fem file first for spcs
        vals = self.split_components(line)
        try:
            getattr(self, mode)[vals[1]] = {} # subcase dict
            getattr(self, mode)[vals[1]][vals[2]] = {} # sid dict
            getattr(self, mode)[vals[1]][vals[3]] = {}
        except:
            raise Exception(f"Couldn't read {mode} data.")

    def read_spc(self, line, mode):
        """self.spc dict
        {
            subcaseid:{
                    sid:{
                        nid: component num. -> ['1','2'] -> constrained in x,y
                    }
                }
        }
        """
        vals = self.split_components(line)
        try:
            for sub_id in self.spc.keys():
                for sid in self.spc[sub_id].keys():
                    if vals[1] == sid:
                        self.spc[sub_id][sid][f"7{vals[2][2:]}"] = list(vals[3])
            ## skipped value of enforced motion bcz all spcs r same
        except:
            raise Exception(f"Couldn't access/modify {mode} data.")

    def read_disp(self, line, sub_id):
        vals = [i.strip() for i in line.split(' ') if i]
        self.outputs[sub_id][vals[0]] = vals[2:]

    def rm_nodes_with_no_types(self, no_types):
        for nid in no_types:
            del self.node[nid]

    def organize_data(self):
        """self.node dict
        {
            nid:{
                    'data': coords,
                    'type': tria | rb2,rb3 (master,slave); 5 types
                    'thickness': given for trias, undefined for rb2,rb3 master nodes
                }
        }
        """

        for eid,data in self.tria.items():
            data = data['data']
            pid = data[0]
            node_ids = data[1:]
            for node_id in node_ids:
                self.node[node_id]['type'] = 'tria'
                self.node[node_id]['thickness'] = self.pshell[pid]['data'][1] # 2nd elements in data dict is thickness for pshell

        ######### WARNING: what about their thickness
        # as slave nodes are part of shell , they have thickness defined thru trias
        for eid,data in self.rb2.items():
            slave_nids = data['data'][2:] # slave nodes
            master_nid =  data['data'][0]
            ## leaving out the CM value at data['data'][1]
            self.node[master_nid]['type'] = 'rb2_master'
            self.node[master_nid]['thickness'] = '0'
            for nid in slave_nids:
                self.node[nid]['type'] = 'rb2_slave'
        
        for eid,data in self.rb3.items():
            slave_nids = data['data'][4:] # slave nodes
            master_nid =  data['data'][0]
            ## leaving out the refc, wt1, c1
            self.node[master_nid]['type'] = 'rb3_master'
            self.node[master_nid]['thickness'] = '0'
            for nid in slave_nids:
                self.node[nid]['type'] = 'rb3_slave'

        no_types = list(k for k,node in self.node.items() if 'type' not in node.keys())
        self.rm_nodes_with_no_types(no_types)

        for nid in self.node.keys():
            self.node[nid]['spc'] = [0, 0, 0]
            self.node[nid]['force'] = [0, 0, 0]

        for sub_id in self.spc.keys():
            node_copy = copy.deepcopy(self.node)
            for sid in self.spc[sub_id]:
                for nid,comps in self.spc[sub_id][sid].items():
                    dof_constraints = [int(i) for i in comps]  
                    for dof in dof_constraints:
                        node_copy[nid]['spc'][dof - 1] = 1
            for force_id, force_data in self.force.items():
                nid = force_data['nid']
                if nid in node_copy:  # Only apply force if node is valid
                    node_copy[nid]['force'] = force_data['force']
            self.inputs[sub_id] = node_copy

        for sub_id in self.outputs.keys():
            for nid,disps in self.outputs[sub_id].items():
                if nid in self.inputs[sub_id].keys():
                    self.inputs[sub_id][nid]['y'] = disps

# r = ReadRawData()
# t1 = "MAT1    31100012 210000.             0.3  7.85-9"
# rb3 = ["RBE3    28949129           74002  123456      1.     1232885023428850273", 
#       "+       2885026728850304288502292885027028850266288503032885023328850314",
#       "+       2885027628850313288502392885031828850170288503342885022128850296",
#       "+       2885033328850222288501812885021828850329288502782885021728850235",
#       "+       2885017528850174288502062885016928850328288501802885022528850205",
#       "+       2885024028850178288502482885022628850263288502472885021528850243",
#       "+       2885028028850317288503202885024628850194288501772885021428850193",
#       "+       2885027728850327288503322885029728850265288502282885029828850331",
#       "+       2885024228850325288503192885033028850326288502532885020828850281",
#       "+       288503012885026428850207288503112885030228850312"]
# rid = r.read_rbe(rb3[0], "rb3")
# for i in range(1,10):
#     r.read_rbe(rb3[i], 'rb3', True, rid)
# import numpy as np
# print(r.rb3, len(np.unique(r.rb3[rid]['data'])))
# spcadd = "SPCADD       805     900     905"
# s1 = "SPC          900  604001       3      0."
# s2 = "SPC          905  404000      12      0."
# r.read_spc_subcase(spcadd, 'spc')
# r.read_spc(s1, 'spc')
# r.read_spc(s2, 'spc')
# print(r.spc)
# s3 = "SPC          906  424001      12      0."
# r.read_spc(s3, 'spc')