import argparse
import sys
import yaml
from src.ingestion.ingest import run_ingestion
from src.transformation.run_all_transformations import main as run_transfo
from src.prediction.training_pipeline import train
from src.prediction.predictor import predict


def cli():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--step",
        choices=["all", "ingest", "transform", "train", "predict"],
        default="all",
    )
    p.add_argument(
        "--mode",
        choices=["api", "fake"],
        default=None,
        help="Force un mode (outre config.yml)",
    )
    p.add_argument("--input", help="Fichier pour --step predict")
    p.add_argument("--output", help="Fichier pour --step predict")
    args = p.parse_args()

    # surcharge dynamique
    if args.mode:
        cfg = yaml.safe_load(open("config.yml"))
        cfg["mode"] = args.mode
        yaml.safe_dump(cfg, open("config.yml", "w"))

    if args.step in ("all", "ingest"):
        run_ingestion()
    if args.step in ("all", "transform"):
        run_transfo()
    if args.step in ("all", "train"):
        train()
    if args.step in ("all", "predict"):
        if args.input and args.output:
            predict(args.input, args.output)
        else:
            print(predict().head())


if __name__ == "__main__":
    cli()