from argparse import ArgumentParser
from utils.common import get_config
from preprocessing import generate_bc_VFG, generate_CDG
from preprocessing import cdg_preprocess
from preprocessing.cdg_generator import generate_CDG, generate_CDG_osp
from preprocessing.cfg_generator import generate_CFG, generate_CFG_osp
from preprocessing.dot_generator import generate_bc_VFG, generate_bc_VFG_osp, generate_VFG
import os
from utils.common import CWEID_AVA, CWEID_ADOPT
from preprocessing import token_preprocess
from scripts.generate_sample_all import sard_preprocess_all, sard_generate_all, sard_preprocess_CWE, sard_generate_CWE, preprocess_osp
from preprocessing import c2s_preprocess
from utils.xml_parser import get_total_label, getCodeIDtoPathDict_osp, create_osp_source_code ,create_d2a_source_code
from os.path import join
import xml.etree.ElementTree as ET
import json
if __name__ == "__main__":
    # create_d2a_source_code()
    # # python preprocess.py --cweid 119
    # arg_parser = ArgumentParser()
    # # arg_parser.add_argument("--cweid", type=str, default=None)
    # arg_parser.add_argument("--project", type=str, default=None)
    # args = arg_parser.parse_args()
    # generate_VFG("/home/chengxiao/dataset/vul/CWE", "CWE710")
    # generate_bc_VFG("/home/chengxiao/dataset/vul", "CWE707")
    # sard_generate_CWE("CWE710")
    # sard_generate_CWE("CWE707")


    root = '/home/chengxiao/project/vul_detect/data_d2a/sysevr'
    for bug_type in os.listdir(root):
        if 'train.txt' in os.listdir(os.path.join(root,bug_type)):
            continue
        try:
            preprocess_osp(bug_type)
        except Exception as e:
            with open('preprocess_sys_d2a_error.log', 'a') as f:
                f.write(bug_type+'\n')
                f.write(str(e)+'\n')
                f.close()
    # create_d2a_source_code()
    # preprocess_osp('BIABD_USE_AFTER_FREE')
    # sard_preprocess_CWE("CWE707")
    # get_total_label()
    # source = '/home/chengxiao/project/astminer/token_result/v2'
    # target = '/home/chengxiao/project/vul_detect/data/token'
    # token_preprocess.merge_csv_to_txt(source,target)
    # for cwe_id in ["CWE20"]:
    #     print(cwe_id)
    #     _config = get_config("token", cwe_id)
    #     token_preprocess.preprocess(_config)

    # _config = get_config("vgdetector", "redis")
    # generatie_CFG_osp(_config)
