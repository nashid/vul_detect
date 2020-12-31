from argparse import ArgumentParser
from utils.common import get_config
from preprocessing import generate_bc_VFG, generate_CDG
from preprocessing.cdg_preprocess import preprocess
from preprocessing.cdg_generator import generate_CDG, generate_CDG_osp
from preprocessing.cfg_generator import generate_CFG, generate_CFG_osp
from preprocessing.dot_generator import generate_bc_VFG, generate_bc_VFG_osp,generate_VFG_osp
import os
from preprocessing.token_preprocess import preprocess, split_dataset
from utils.common import CWEID_AVA

if __name__ == "__main__":
    # python preprocess.py --cweid 119
    arg_parser = ArgumentParser()
    # arg_parser.add_argument("--cweid", type=str, default=None)
    arg_parser.add_argument("--project", type=str, default=None)
    args = arg_parser.parse_args()
    _config = get_config("vuldeepecker", args.project)
    # _config = get_config("vuldeepecker", "CWE20")
    # preprocess(_config)
    # split_dataset(_config)
    # generateCDG(_config, "CWE20")
    # for cweid in CWEID_AVA:
    # _config = get_config("token", cweid)
    # generate_bc_VFG_osp(_config, args.project)
    generate_CDG_osp(_config)
    # generate_VFG_osp(os.path.join(_config.raw_data_folder,"CVE"), 'openssl')
    # generate_bc_VFG_osp(_config, 'openssl')
