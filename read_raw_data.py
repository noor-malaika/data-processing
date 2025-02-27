###NOTE: This script uses a lot of indexing, couldn't be understood without references (CBUSH_FORCE_SPC.nas, FYP_model.nas)
"""spc and force components r same everywhere, don't need to read them for all variants"""
from itertools import combinations
import copy

class ReadRawData:
    def __init__(self):
        self.nodal_features = {}
        self.node = {}
        self.edge_features = {}
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

    def _create_tria_edges(self):
        tria_edges = set()

        # --- TRIA ELEMENTS ---
        for eid, data in self.tria.items():
            self.edge_features[eid] = {}
            nids = data['data'][1:]

            if len(nids) != 3:  # Ensure tria has exactly 3 nodes
                raise(f"Warning: TRIA {eid} has incorrect node count: {len(nids)}")

            temp_edges = list(combinations(nids, 2))  # All possible 2-node edges in tria
            for i, edge in enumerate(temp_edges):
                edge = tuple(sorted(edge))  # Sort to maintain consistency

                if edge not in tria_edges:
                    tria_edges.add(edge)  # Store unique edges
                    self.edge_features[eid][i] = {'edge': edge, 'edge_type': 'tria'}

        print(f"Total Unique Tria Edges: {len(tria_edges)}")

    def _create_rb2_edges(self):
        # --- RB2 ELEMENTS ---
        for eid, data in self.rb2.items():
            self.edge_features[eid] = {}
            master_id = data['data'][0]
            slave_ids = data['data'][2:]

            if master_id is None or not slave_ids:  # Ensure data is valid
                raise(f"Warning: RB2 {eid} has missing master/slave data")

            for i, sl_id in enumerate(slave_ids):
                self.edge_features[eid][i] = {'edge': (master_id, sl_id), 'edge_type': 'rb2'}

    def _create_rb3_edges(self):
        # --- RB3 ELEMENTS ---
        for eid, data in self.rb3.items():
            self.edge_features[eid] = {}
            master_id = data['data'][0]
            slave_ids = data['data'][4:]

            if master_id is None or not slave_ids:  # Ensure data is valid
                raise(f"Warning: RB3 {eid} has missing master/slave data")

            for i, sl_id in enumerate(slave_ids):
                self.edge_features[eid][i] = {'edge': (master_id, sl_id), 'edge_type': 'rb3'}

    def create_edges(self):
        """
        Extracts edges from tria, rb2, and rb3 elements while ensuring correctness.
        """

        self._create_tria_edges()
        self._create_rb2_edges()
        self._create_rb3_edges()

        # --- FINAL VALIDATION ---
        total_edges = sum(len(edges) for edges in self.edge_features.values())
        print(f"Total Extracted Edges: {total_edges}")

        # return self.edge_features  # Return edges for debugging if needed

    def _add_tria_nodes(self):
        for eid,data in self.tria.items():
            data = data['data']
            pid = data[0]
            node_ids = data[1:]
            for node_id in node_ids:
                self.node[node_id]['type'] = 'tria'
                self.node[node_id]['thickness'] = self.pshell[pid]['data'][1] # 2nd elements in data dict is thickness for pshell

    def _add_rb2_nodes(self):
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

    def _add_rb3_nodes(self):
        for eid,data in self.rb3.items():
            slave_nids = data['data'][4:] # slave nodes
            master_nid =  data['data'][0]
            ## leaving out the refc, wt1, c1
            self.node[master_nid]['type'] = 'rb3_master'
            self.node[master_nid]['thickness'] = '0'
            for nid in slave_nids:
                self.node[nid]['type'] = 'rb3_slave'

    def _add_spc_and_force(self):
        # initializing empty force and spc features for all nodes
        for nid in self.node.keys():
            self.node[nid]['spc'] = [0, 0, 0]
            self.node[nid]['force'] = [0, 0, 0]

        # assigning the (specific nodes) spc and force values - based on extracted dicts
        for sub_id in self.spc.keys():
            node_copy = copy.deepcopy(self.node)
            for sid in self.spc[sub_id]:
                for nid,comps in self.spc[sub_id][sid].items():
                    dof_constraints = [int(i) for i in comps]  
                    for dof in dof_constraints:
                        node_copy[nid]['spc'][dof - 1] = 1
            
            self.nodal_features[sub_id] = node_copy
            force_node_id = self.force[sub_id]['nid']
            self.nodal_features[sub_id][force_node_id]['force'] = self.force[sub_id]['force']


    def _set_zero_disp_for_constrained_nodes(self):
        # setting disp to 0 at nodes with spc - those are small (e.g. 10^-18)
        for sub_id in self.spc.keys():
            for sid in self.spc[sub_id]:
                for nid,comps in self.spc[sub_id][sid].items():
                    if nid in self.nodal_features[sub_id].keys():
                        # ids to replace displacements which have spc constraints
                        comp_ids = [int(comps[i]) - 1 if i < len(comps) and comps[i] else None for i in range(3)]
                        # Update 'y' values based on comp_ids
                        self.nodal_features[sub_id][nid]['y'] = [
                            0 if i in comp_ids else self.nodal_features[sub_id][nid]['y'][i] for i in range(3)
                        ]


    def _add_displacements_as_outputs(self):
        # adding displacements as nodal properties (y - output features)
        for sub_id in self.outputs.keys():
            for nid,disps in self.outputs[sub_id].items():
                if nid in self.nodal_features[sub_id].keys():
                    self.nodal_features[sub_id][nid]['y'] = disps

        self._set_zero_disp_for_constrained_nodes()


    def create_node_features(self):
        """self.node dict
        {
            nid:{
                    'data': coords,
                    'type': tria | rb2,rb3 (master,slave); 5 types
                    'thickness': given for trias, undefined for rb2,rb3 master nodes
                }
        }
        """
        # assigning element types and thicknesses
        self._add_tria_nodes()
        self._add_rb2_nodes()
        self._add_rb3_nodes()

        # removing nodes which dont have any type - left with (tria, rb2, rb3)
        no_types = list(k for k,node in self.node.items() if 'type' not in node.keys())
        self.rm_nodes_with_no_types(no_types)

        # adding spc and force to node features
        self._add_spc_and_force()

        # adding displacements for outputs
        self._add_displacements_as_outputs()


    def organize(self):
        self.create_node_features()
        self.create_edges()