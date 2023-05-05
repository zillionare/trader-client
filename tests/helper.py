import json
import os
import pickle

import cfg4py
import pandas as pd
from coretypes import FrameType
from omicron import tf
from omicron.dal.influx.influxclient import InfluxClient
from omicron.models.stock import Stock


def data_dir():
    return os.path.join(os.path.dirname(__file__), "data")


async def data_populate():
    cfg = cfg4py.init(data_dir())
    url, token, bucket, org = (
        cfg.influxdb.url,
        cfg.influxdb.token,
        cfg.influxdb.bucket_name,
        cfg.influxdb.org,
    )
    client = InfluxClient(url, token, bucket, org)

    # fill in influxdb
    await client.drop_measurement("stock_bars_1d")
    await client.drop_measurement("stock_bars_1m")

    for ft in (FrameType.MIN1, FrameType.DAY):
        file = os.path.join(data_dir(), f"bars_{ft.value}.pkl")
        with open(file, "rb") as f:
            bars = pickle.load(f)
            await Stock.persist_bars(ft, bars)

    df = pd.read_csv(
        os.path.join(data_dir(), "limits.csv"), sep="    ", parse_dates=["time"]
    )
    limits = df.to_records(index=False)
    limits.dtype.names = ["frame", "code", "high_limit", "low_limit"]
    await Stock.save_trade_price_limits(limits, False)

    with open(os.path.join(data_dir(), "calendar.json"), "r") as f:
        frames = json.load(f)
        tf.day_frames = frames["day_frames"]
