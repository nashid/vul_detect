from argparse import ArgumentParser
from utils.common import get_config
from preprocessing import generate_bc_VFG, generate_CDG
from preprocessing import cdg_preprocess
from preprocessing.cdg_generator import generate_CDG, generate_CDG_osp
from preprocessing.cfg_generator import generate_CFG, generate_CFG_osp
from preprocessing.dot_generator import generate_bc_VFG, generate_bc_VFG_osp
from preprocessing.sys_generator import generate_SYS, generate_SYS_osp
from preprocessing.mulvdp_generator import generate_MULVDP, generate_MULVDP_osp
from preprocessing import mulvdp_preprocess
from preprocessing import sys_preprocess
import os
from utils.common import CWEID_AVA
from preprocessing import token_preprocess
from preprocessing import c2s_preprocess, c2v_preprocess


def sard_generate_all(approach):
    sard_generate_models = {
        "vuldeepecker": generate_CDG,
        "vgdetector": generate_CFG,
        "sysevr": generate_SYS,
        "mulvuldeepecker": generate_MULVDP
    }
    if approach not in sard_generate_models:
        print(
            f"Unknown model: {approach}, try on of {sard_generate_models.keys()}"
        )
        return

    for cweid in CWEID_AVA:
        _config = get_config(approach, cweid)
        sard_generate_models[approach](_config)


def sard_preprocess_all(approach):
    sard_preprocess_models = {
        "token": token_preprocess.preprocess,
        "vuldeepecker": cdg_preprocess.preprocess,
        "sysevr": sys_preprocess.preprocess,
        "mulvuldeepecker": mulvdp_preprocess.preprocess,
        "code2seq": c2s_preprocess.preprocess,
        "code2vec": c2v_preprocess.preprocess
    }
    if approach not in sard_preprocess_models:
        print(
            f"Unknown model: {approach}, try on of {sard_preprocess_models.keys()}"
        )
        return

    for cweid in CWEID_AVA:
        print(f"processing {cweid}")
        _config = get_config(approach, cweid)
        sard_preprocess_models[approach](_config)
