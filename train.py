from argparse import ArgumentParser
import os
from os.path import join
from typing import Tuple

import torch
from omegaconf import DictConfig
from pytorch_lightning import seed_everything, Trainer, LightningModule, LightningDataModule
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor
from pytorch_lightning.loggers import WandbLogger, TensorBoardLogger

from models import TOKEN_BLSTM, VDP_BLSTM, SYS_BLSTM, SYSDataModule, VGD_GNN, TokenDataModule, VDPDataModule, VGDDataModule, MulVDP_BLSTM, MulVDPDataModule, Code2SeqAttn, C2SPathContextDataModule, Code2VecAttn, C2VPathContextDataModule

from utils.callback import UploadCheckpointCallback, PrintEpochResultCallback
from utils.common import print_config, filter_warnings, get_config
from utils.vocabulary import Vocabulary_token, Vocabulary_c2s


def get_C2S(
        config: DictConfig, vocabulary: Vocabulary_c2s
) -> Tuple[LightningModule, LightningDataModule]:
    model = Code2SeqAttn(config, vocabulary)
    data_module = C2SPathContextDataModule(config, vocabulary)
    return model, data_module


def get_C2V(
        config: DictConfig, vocabulary: Vocabulary_c2s
) -> Tuple[LightningModule, LightningDataModule]:
    model = Code2VecAttn(config, vocabulary)
    data_module = C2VPathContextDataModule(config, vocabulary)
    return model, data_module


def get_MULVDP(
    config: DictConfig, vocabulary: Vocabulary_token
) -> Tuple[LightningModule, LightningDataModule]:
    model = MulVDP_BLSTM(config, vocabulary)
    data_module = MulVDPDataModule(config, vocabulary)
    return model, data_module


def get_token_based(
    config: DictConfig, vocabulary: Vocabulary_token
) -> Tuple[LightningModule, LightningDataModule]:
    model = TOKEN_BLSTM(config, vocabulary)
    data_module = TokenDataModule(config, vocabulary)
    return model, data_module


def get_VDP(
    config: DictConfig, vocabulary: Vocabulary_token
) -> Tuple[LightningModule, LightningDataModule]:
    model = VDP_BLSTM(config, vocabulary)
    data_module = VDPDataModule(config, vocabulary)
    return model, data_module


def get_VGD(
    config: DictConfig, vocabulary: Vocabulary_token
) -> Tuple[LightningModule, LightningDataModule]:
    model = VGD_GNN(config, vocabulary)
    data_module = VGDDataModule(config, vocabulary)
    return model, data_module


def get_SYS(
    config: DictConfig, vocabulary: Vocabulary_token
) -> Tuple[LightningModule, LightningDataModule]:
    model = SYS_BLSTM(config, vocabulary)
    data_module = SYSDataModule(config, vocabulary)
    return model, data_module


def train(config: DictConfig, resume_from_checkpoint: str = None):
    filter_warnings()
    print_config(config)
    seed_everything(config.seed)

    known_models = {
        "token": get_token_based,
        "vuldeepecker": get_VDP,
        "vgdetector": get_VGD,
        "sysevr": get_SYS,
        "mulvuldeepecker": get_MULVDP,
        "code2seq": get_C2S,
        "code2vec": get_C2V
    }

    vocab = {
        "token": Vocabulary_token,
        "vuldeepecker": Vocabulary_token,
        "vgdetector": Vocabulary_token,
        "sysevr": Vocabulary_token,
        "mulvuldeepecker": Vocabulary_token,
        "code2seq": Vocabulary_c2s,
        "code2vec": Vocabulary_c2s
    }
    if config.name not in known_models:
        print(f"Unknown model: {config.name}, try on of {known_models.keys()}")
        return
    if os.path.exists(
            join(config.data_folder, config.name, config.dataset.name,
                 "vocab.pkl")):
        vocabulary = vocab[config.name].load_vocabulary(
            join(config.data_folder, config.name, config.dataset.name,
                 "vocab.pkl"))
    else:
        vocabulary = None
    model, data_module = known_models[config.name](config, vocabulary)
    # define logger
    # wandb logger
    # wandb_logger = WandbLogger(project=f"{config.name}-{config.dataset.name}",
    #                            log_model=True,
    #                            offline=config.log_offline)
    # wandb_logger.watch(model)
    # checkpoint_callback = ModelCheckpoint(
    #     dirpath=wandb_logger.experiment.dir,
    #     filename="{epoch:02d}-{val_loss:.4f}",
    #     period=config.save_every_epoch,
    #     save_top_k=-1,
    # )
    # upload_checkpoint_callback = UploadCheckpointCallback(
    #     wandb_logger.experiment.dir)

    # tensorboard logger
    tensorlogger = TensorBoardLogger(join("ts_logger", config.name),
                                     config.dataset.name)
    # define model checkpoint callback
    checkpoint_callback = ModelCheckpoint(
        dirpath=join(tensorlogger.log_dir, "checkpoints"),
        monitor="val_loss",
        filename="{epoch:02d}-{val_loss:.4f}",
        period=config.save_every_epoch,
        save_top_k=3,
    )
    upload_checkpoint_callback = UploadCheckpointCallback(
        join(tensorlogger.log_dir, "checkpoints"))


    # define early stopping callback
    early_stopping_callback = EarlyStopping(
        patience=config.hyper_parameters.patience,
        monitor="val_loss",
        verbose=True,
        mode="min")
    # define callback for printing intermediate result
    print_epoch_result_callback = PrintEpochResultCallback("train", "val")
    # use gpu if it exists
    gpu = 1 if torch.cuda.is_available() else None
    # define learning rate logger
    lr_logger = LearningRateMonitor("step")
    trainer = Trainer(
        max_epochs=config.hyper_parameters.n_epochs,
        gradient_clip_val=config.hyper_parameters.clip_norm,
        deterministic=True,
        check_val_every_n_epoch=config.val_every_epoch,
        log_every_n_steps=config.log_every_epoch,
        logger=[tensorlogger],
        reload_dataloaders_every_epoch=config.hyper_parameters.
        reload_dataloader,
        gpus=gpu,
        progress_bar_refresh_rate=config.progress_bar_refresh_rate,
        callbacks=[
            lr_logger, early_stopping_callback, checkpoint_callback,
            print_epoch_result_callback, upload_checkpoint_callback
        ],
        resume_from_checkpoint=resume_from_checkpoint,
    )

    trainer.fit(model=model, datamodule=data_module)
    trainer.test()


if __name__ == "__main__":
    # python train.py token --dataset CWE119
    arg_parser = ArgumentParser()
    arg_parser.add_argument("model", type=str)
    arg_parser.add_argument("--dataset", type=str, default=None)
    arg_parser.add_argument("--offline", action="store_true")
    arg_parser.add_argument("--resume", type=str, default=None)
    args = arg_parser.parse_args()

    _config = get_config(args.model, args.dataset, log_offline=args.offline)
    train(_config, args.resume)
