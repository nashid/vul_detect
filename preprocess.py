from argparse import ArgumentParser
from utils.common import get_config
from preprocessing import generate_bc_VFG, generate_CDG
from preprocessing import cdg_preprocess
from preprocessing.cdg_generator import generate_CDG, generate_CDG_osp
from preprocessing.cfg_generator import generate_CFG, generate_CFG_osp
from preprocessing.dot_generator import generate_bc_VFG, generate_bc_VFG_osp
import os
from utils.common import CWEID_AVA
from preprocessing import token_preprocess
from scripts.generate_sample_all import sard_preprocess_all, sard_generate_all
from preprocessing import c2s_preprocess

if __name__ == "__main__":
    # # python preprocess.py --cweid 119
    # arg_parser = ArgumentParser()
    # # arg_parser.add_argument("--cweid", type=str, default=None)
    # arg_parser.add_argument("--project", type=str, default=None)
    # args = arg_parser.parse_args()
    sard_preprocess_all("code2vec")
