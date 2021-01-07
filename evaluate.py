from argparse import ArgumentParser
from typing import Tuple

import torch
from omegaconf import DictConfig
from pytorch_lightning import Trainer, seed_everything

from models import TOKEN_BLSTM, VDP_BLSTM, SYS_BGRU, SYSDataModule, VGD_GNN, TokenDataModule, VDPDataModule, VGDDataModule, MulVDP_BLSTM, MulVDPDataModule, Code2SeqAttn, C2SPathContextDataModule, Code2VecAttn, C2VPathContextDataModule

from utils.vocabulary import Vocabulary_c2s, Vocabulary_token


def load_code2seq(
    checkpoint_path: str, config: DictConfig, vocabulary: Vocabulary_c2s
) -> Tuple[Code2SeqAttn, C2SPathContextDataModule]:
    model = Code2SeqAttn.load_from_checkpoint(checkpoint_path=checkpoint_path)
    data_module = C2SPathContextDataModule(config, vocabulary)
    return model, data_module


def load_code2class(
        checkpoint_path: str, config: DictConfig,
        vocabulary: Vocabulary_c2s) -> Tuple[Code2VecAttn, C2VPathContextDataModule]:
    model = Code2VecAttn.load_from_checkpoint(checkpoint_path=checkpoint_path)
    data_module = C2VPathContextDataModule(config, vocabulary)
    return model, data_module


def load_mulvuldeepecker(
    checkpoint_path: str, config: DictConfig, vocabulary: Vocabulary_token
) -> Tuple[MulVDP_BLSTM, MulVDPDataModule]:
    model = MulVDP_BLSTM.load_from_checkpoint(checkpoint_path=checkpoint_path)
    data_module = MulVDPDataModule(config, vocabulary)
    return model, data_module


KNOWN_MODELS = {
    "code2seq": load_code2seq,
    "code2class": load_code2class,
    "mulvuldeepecker": load_mulvuldeepecker
}


def test(checkpoint_path: str,
         data_folder: str = None,
         batch_size: int = None):
    checkpoint = torch.load(checkpoint_path, map_location=torch.device("cpu"))
    config = checkpoint["hyper_parameters"]["config"]
    vocabulary = checkpoint["hyper_parameters"]["vocabulary"]
    if data_folder is not None:
        config.data_folder = data_folder
    if batch_size is not None:
        config.hyper_parameters.test_batch_size = batch_size

    if config.name not in KNOWN_MODELS:
        print(
            f"Unknown model {config.name}, try one of {' '.join(KNOWN_MODELS.keys())}"
        )
        return
    model, data_module = KNOWN_MODELS[config.name](checkpoint_path, config,
                                                   vocabulary)

    seed_everything(config.seed)
    gpu = 1 if torch.cuda.is_available() else None
    trainer = Trainer(gpus=gpu)
    trainer.test(model, datamodule=data_module)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("checkpoint", type=str)
    arg_parser.add_argument("--data-folder", type=str, default=None)
    arg_parser.add_argument("--batch-size", type=int, default=None)

    args = arg_parser.parse_args()

    test(args.checkpoint, args.data_folder, args.batch_size)
