from src.ingestion.ingest import run_ingestion
import yaml, shutil, pathlib

def test_fake_ingestion(tmp_path):
    cfg = yaml.safe_load(open("config.yml"))
    cfg["mode"] = "fake"
    yaml.safe_dump(cfg, open("config.test.yml", "w"))
    run_ingestion("config.test.yml")
    assert (pathlib.Path("data/raw") / "elections.parquet").exists()
    shutil.rmtree("data/raw")
